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

from ingestor.datapipe.steps.base_step import DefaultTransformStep

import pandas as pd

from datetime import datetime
import geopandas as gpd
import os
import importlib

import os
import django
from django.contrib.gis.geos import GEOSGeometry
from shapely.wkt import dumps as shapely_to_wkt
from ingestor.utils.geo_districts import CityDistrictsDecoder


class OSMTransformStep(DefaultTransformStep):
    """OSM-specific transform step."""

    ATTR_MAPPING = {"yes": "Ja", "no": "Nein", "customers": "Kunden", "private": "Privat",
                    "permissive": "Erlaubt", "ja": "Ja", "nein": "Nein"}

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        gdf = gpd.read_file(download_file)

        gdf = gdf[gdf.geometry.type.isin(["Point", "Polygon", "MultiPolygon"])]
        
        if db_model.__name__ == "OsmRecyclingCenter":
            gdf = gdf[gdf['recycling_type'] == 'centre']
        elif db_model.__name__ == "OsmRecyclingContainer":
            gdf = gdf[gdf['recycling_type'] == 'container']
        elif db_model.__name__ == "OsmSportCenterClimbing":
            gdf = gdf[gdf['sport'] == 'climbing']
        elif db_model.__name__ == "OsmSportCenterSwimming":
            gdf = gdf[gdf['sport'] == 'swimming']
        elif db_model.__name__ == "OsmVendingMachineParkingTicket":
            gdf = gdf[gdf['vending'] == 'parking_tickets']
        elif db_model.__name__ == "OsmVendingMachineDogToilet":
            gdf = gdf[gdf['vending'] == 'excrement_bags']

        rows_as_dict = gdf.to_dict(orient='records')

        result = []
        for row in rows_as_dict:

            row = {key.replace(":", "_"):
                    OSMTransformStep.ATTR_MAPPING.get(value, value) if isinstance(value, str) else value
                   for key, value in row.items()}

            fields = {
                field.name: row.get(field.name)
                for field in db_model._meta.fields
                if field.name in row
            }

            fields["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(fields["geometry"])
            fields["data_source"] = context.resource.data_source
            fields["data_acquisition_date"] = data_acquisition_date
            result.append(fields)
        return result