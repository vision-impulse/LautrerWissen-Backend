# Copyright (c) 2025 Vision Impulse GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Authors: Benjamin Bischke

import os.path
import pandas as pd
import requests
import geopandas as gpd
import logging
from shapely.ops import unary_union
from geopandas.tools import sjoin
from shapely.geometry import shape
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.wkb import loads as load_wkb
from pyproj import CRS
from ingestor.utils.geo import clean_geometries
from ingestor.datapipe.utils.django_integration import get_django_model

logger = logging.getLogger("webapp")

DEFAULT_LOCAL_CRS = "EPSG:25832"
TARGET_CRS = "EPSG:4326"


def _get_local_aea(center_lat: float, center_lon: float) -> CRS:
    """
    Lokales Albers‑Equal‑Area CRS für metrische Operationen.
    """
    lat1, lat2 = center_lat - 4, center_lat + 4          # Standard‑Parallel‑Paar
    return CRS.from_proj4(
        f"+proj=aea +lat_0={center_lat:.6f} +lon_0={center_lon:.6f} "
        f"+lat_1={lat1:.6f} +lat_2={lat2:.6f} "
        f"+x_0=0 +y_0=0 +units=m +ellps=WGS84 +no_defs"
    )

def _empty_districts_gdf():
    """
    Standardized empty GeoDataFrame.
    """
    return gpd.GeoDataFrame(
        columns=["Name", "geometry"],
        geometry="geometry",
        crs=TARGET_CRS,
    )


def load_districts():
    """
    Load districts from Django ORM into GeoDataFrame.
    Always returns valid GeoDataFrame in EPSG:4326.
    Never raises.
    """

    try:
        District = get_django_model(
            "KLCityDistrict",
            django_app="lautrer_wissen",
        )
        if District is None:
            return _empty_districts_gdf()
        queryset = District.objects.all()

        if not queryset.exists():
            logger.info("District table is empty.")
            return _empty_districts_gdf()

        rows = []
        for obj in queryset:
            geom = getattr(obj, "geometry", None)
            if geom is None:
                continue
            try:
                # Convert GeoDjango GEOSGeometry -> Shapely geometry
                shapely_geom = load_wkb(bytes(geom.wkb))
            except Exception:
                logger.debug(
                    "Skipping invalid geometry for object %s",
                    obj.pk,
                    exc_info=True,
                )
                continue
            rows.append({
                "Name": getattr(obj, "name", None),
                "geometry": shapely_geom,
            })
        gdf = gpd.GeoDataFrame(
            rows,
            geometry="geometry",
        )

        gdf = gdf.set_crs(DEFAULT_LOCAL_CRS)
        gdf = clean_geometries(gdf)
        if gdf.empty:
            logger.info("All district geometries invalid.")
            return _empty_districts_gdf()
        if gdf.crs != TARGET_CRS:
            gdf = gdf.to_crs(TARGET_CRS)
        return gdf.copy()
    except Exception:
        logger.exception("Failed loading districts from Django.")
        return _empty_districts_gdf()
    


class CityDistrictsDecoder(object):

    @staticmethod
    def _to_target_crs(geom):
        """
        Returns the geometry in EPSG:4326.
        Shapely objects have no CRS, so caller must tell
        if conversion is needed; we assume EPSG:4326 by default.
        """
        if isinstance(geom, (Point, Polygon, MultiPolygon)):
            return geom  # treat as already WGS‑84
        
        # If the caller passes a GeoSeries/GeoDataFrame row with a CRS
        # convert via GeoSeries to keep it simple:
        if hasattr(geom, "crs") and geom.crs and geom.crs != 4326:
            return gpd.GeoSeries([geom]).set_crs(geom.crs).to_crs(4326).iloc[0]
        return geom
    
    @staticmethod
    def get_district_name_for_geometry(geom):
        districts = load_districts()
        if geom is None or districts is None:
            return "Unbekannt"
        
        geom_wgs = CityDistrictsDecoder._to_target_crs(geom)
        names = districts.loc[districts.geometry.intersects(geom_wgs), "Name"].unique()
        return ", ".join(sorted(names)) if names.size else "Kreis Kaiserslautern"

    @staticmethod
    def filter_points_by_city_polygon(geoms_proj: gpd.GeoDataFrame,
                                      buffer_km: float = 0):
        """
        Returns geometries that lie *within* the city‑district polygons, optionally
        enlarged by `buffer_km`.

        Parameters
        ----------
        geoms_proj : GeoDataFrame
            geometries to filter.
        buffer_km : float, default 0
            Radial buffer (in kilometres) to enlarge the polygons before testing.
        """
        # ── Ensure CRS for polygons & points ───────────────────────────────
        districts = load_districts()
        if districts is None or districts.empty:
            logger.info("No districts found for filtering step, returning original data!")
            return geoms_proj

        poly_gdf = districts.to_crs(epsg=4326)
        poly_gdf = poly_gdf.dissolve()

        if not poly_gdf.crs or not poly_gdf.crs.is_geographic:
            poly_gdf = poly_gdf.to_crs(epsg=4326)

        # ── Optional polygon buffer (in metres) ────────────────────────────
        if buffer_km:
            # Choose a local equal‑area projection centred on the polygon extent
            west, south, east, north = poly_gdf.total_bounds
            center_lon = (west + east) / 2
            center_lat = (south + north) / 2
            aea_crs = _get_local_aea(center_lat, center_lon)
            poly_metric = poly_gdf.to_crs(aea_crs)
            poly_metric["geometry"] = poly_metric.buffer(buffer_km * 1_000)
            poly_gdf = poly_metric.to_crs(4326)  # back to geographic

        # ── Re‑project points to match polygons, run spatial join ──────────
        if geoms_proj.crs is None:
            geoms_proj = geoms_proj.set_crs(4326, allow_override=True)
        pts_orig_crs = geoms_proj.crs

        geoms_proj = geoms_proj.to_crs(poly_gdf.crs)        

        pts_mask   = geoms_proj.geometry.type.isin({"Point", "MultiPoint"})
        pts_join   = sjoin(geoms_proj[pts_mask], poly_gdf,
                        how="inner", predicate="within")
        poly_mask  = ~pts_mask           
        poly_join  = sjoin(geoms_proj[poly_mask], poly_gdf,
                        how="inner", predicate="intersects")

        joined = (
            gpd.GeoDataFrame(pd.concat([pts_join, poly_join], axis=0))
            .sort_index()
        )

        # ── Return to original CRS of incoming points ──────────────────────
        return joined.to_crs(pts_orig_crs)
    