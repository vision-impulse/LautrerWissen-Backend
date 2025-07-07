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

import os
import geopandas as gpd
import zipfile
from ingestor.datapipe.steps.base_step import DefaultTransformStep
from datetime import datetime
from shapely.geometry import Point
from ingestor.utils.geo_districts import CityDistrictsDecoder
import pandas as pd
import json


class TTNGatewayTransformStep(DefaultTransformStep):

    ATTR_MAPPING = {
        "id": "gateway_id",
        "netID": "net_id",
        "tenantID": "tenant_id",
        "clusterID": "cluster_id",
        "updatedAt": "updated_at",
        "antennaPlacement": "antenna_placement",
        "antennaCount": "antenna_count",
    }

    @staticmethod
    def map_properties(properties, mapping):
        return {db_field: properties.get(json_key) for json_key, db_field in mapping.items()}

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        with open(download_file, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        result = []
        for idx, row in df.iterrows():
            row['geometry'] = Point(row['location']["longitude"], row['location']["latitude"])
            del row["location"]
            
            row_mapped = TTNGatewayTransformStep.map_properties(row, TTNGatewayTransformStep.ATTR_MAPPING)
            row = {**row, **row_mapped}
            row["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(row["geometry"])
            row["data_source"] = context.resource.data_source
            row["data_acquisition_date"] = data_acquisition_date
            result.append(row)
        return result

