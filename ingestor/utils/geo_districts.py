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
import wget
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
from geopandas.tools import sjoin
from pyproj import CRS

URL = "https://opendata.kaiserslautern.de/dataset/e2757392-39b5-4008-8a0b-5998adcf7238/resource/701101ef-b868-4f49-ab78-86a79139d46c/download/ortsbezirksgrenzen_wgs84.geojson"

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


class CityDistrictsDecoder(object):

    _FILENAME = "ortsbezirksgrenzen_wgs84.geojson"
    _ENV_PATH = os.getenv("APP_DATA_DIR", "./data/") # Fallback    
    _POLYGON_DISTRICT_FILE = os.path.join(_ENV_PATH, "initial/data/" + _FILENAME)

    if not os.path.exists(_POLYGON_DISTRICT_FILE):
        os.makedirs(os.path.dirname(_POLYGON_DISTRICT_FILE))
        wget.download(URL, out=_POLYGON_DISTRICT_FILE)
    _CITY_DISTRICTS = gpd.read_file(_POLYGON_DISTRICT_FILE)
    _CITY_DISTRICTS_4326 = _CITY_DISTRICTS.to_crs(4326)[["Name", "geometry"]]

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
        if geom is None or CityDistrictsDecoder._CITY_DISTRICTS_4326 is None:
            return "Unbekannt"
        
        geom_wgs = CityDistrictsDecoder._to_target_crs(geom)
        districts = CityDistrictsDecoder._CITY_DISTRICTS_4326

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
        poly_gdf = CityDistrictsDecoder._CITY_DISTRICTS.to_crs(epsg=4326)
        poly_gdf = poly_gdf.dissolve()

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
    