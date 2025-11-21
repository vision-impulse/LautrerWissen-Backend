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
import zipfile

from shapely.geometry import Point
from datetime import datetime
import os
from ingestor.utils.geo_districts import CityDistrictsDecoder


class VRNBusStationTransformStep(DefaultTransformStep):

    COLUMN_MAPPING = {
        'GlobaleID': 'global_id',
        'Name': 'name',
        'Steig GlobaleID': 'platform_global_id',
        'Lat': 'latitude',
        'Lon': 'longitude',
        'Haltestellennummer': 'station_number',
        'Richtung': 'direction',
        'Linien': 'lines',
        'Sitzgelegenheit': 'seating',
        'Abfallbehaelter': 'waste_bin',
        'Beleuchtung': 'lighting'
    }

    ATTR_MAPPING = {"J": "Ja", "N": "Nein"}

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        src_filename = context.resource.source_filename
        result = []

        df, creation_date = self._read_zip_as_df_with_creation_date(download_file, src_filename)

        for idx, row in df.iterrows():
            row['geometry'] = Point(row['longitude'], row['latitude'])
            del row['latitude']
            del row['longitude']
            row["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(row["geometry"])
            row["data_source"] = context.resource.data_source
            row["data_acquisition_date"] = creation_date
            row["seating"] = self.ATTR_MAPPING.get(row["seating"], row["seating"])
            row["waste_bin"] = self.ATTR_MAPPING.get(row["waste_bin"], row["waste_bin"])
            row["lighting"] = self.ATTR_MAPPING.get(row["lighting"], row["lighting"])
            result.append(row)
        return result

    def _read_zip_as_df_with_creation_date(self, zip_file_path, src_filename):
        with zipfile.ZipFile(zip_file_path, 'r') as z:
            file_list = z.namelist()
            csv_file_name = [f for f in file_list if f.startswith(src_filename)][0]

            info = z.getinfo(csv_file_name)
            with z.open(csv_file_name) as csv_file:
                names = ["Haltestellen", "Steige"]
                all_sheets = pd.read_excel(csv_file, sheet_name=names)
                dfs = [df for sn, df in all_sheets.items()]

                df = pd.merge(dfs[0][['GlobaleID', 'Name']],
                              dfs[1][['GlobaleID', 'Steig GlobaleID', 'Lat', 'Lon', 'Haltestellennummer',
                                      'Richtung', 'Linien', 'Sitzgelegenheit', 'Abfallbehaelter', 'Beleuchtung']],
                              on='GlobaleID', how='right')

                df.rename(columns=VRNBusStationTransformStep.COLUMN_MAPPING, inplace=True)
                return df, datetime(*info.date_time)
