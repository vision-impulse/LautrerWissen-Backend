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


class EmergencyPointTransformStep(DefaultTransformStep):

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        src_filename = context.resource.source_filename
        region_filter = context.resource.region_filter
        df, creation_date = self._read_zip_as_df_with_creation_date(download_file, src_filename, region_filter)

        result = []
        for idx, row in df.iterrows():
            row['geometry'] = Point(row['WGS_Laenge'], row['WGS_Breite'])
            del row["WGS_Breite"]
            del row["WGS_Laenge"]

            row["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(row["geometry"])
            row["data_source"] = context.resource.data_source
            row["data_acquisition_date"] = creation_date
            result.append(row)
        return result

    def _read_zip_as_df_with_creation_date(self, zip_file_path, src_filepath, region_filter):
        with zipfile.ZipFile(zip_file_path, 'r') as z:
            file_list = z.namelist()

            # Extract the base name of the shapefile (without path inside the ZIP)
            shp_file_name = [f for f in file_list if f.endswith(src_filepath)][0]
            info = z.getinfo(shp_file_name)
            creation_date = datetime(*info.date_time)

        gdf = gpd.read_file(f"zip://{zip_file_path}!{shp_file_name}")

        df = gdf.rename(columns={
            'RP_Nr': 'rp_nr',
            'Ortsbeschr': 'description',
            'Schild': 'information_sign',
            'Urheber': 'originator',
            'Bundesland': 'federal_state'
        })
        df = df[df['federal_state'] == region_filter]
        return df, creation_date