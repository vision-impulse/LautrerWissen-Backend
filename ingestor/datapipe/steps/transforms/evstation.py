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

import re
import os
import ast
import pandas as pd
import numpy as np

from datetime import datetime
from ingestor.datapipe.steps.base_step import DefaultTransformStep
from ingestor.utils.geo_districts import CityDistrictsDecoder
from shapely.geometry import Point


class EvStationTransformStep(DefaultTransformStep):

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        city_filter =  self._safe_parse_list(context.resource.city_filter)
        df, creation_date_str = self._extract_ladesaeulen_data(download_file)
        creation_date = datetime.strptime(creation_date_str, "%d.%m.%Y").date()

        df = df[df['Kreis/kreisfreie Stadt'].isin(city_filter)]

        rename_map = {
            'Betreiber': 'operator',
            'Anzeigename (Karte)': 'display_name',
            'Straße': 'street',
            'Hausnummer': 'house_number',
            'Adresszusatz': 'address_addition',
            'Postleitzahl': 'postal_code',
            'Ort': 'city',
            'Kreis/kreisfreie Stadt': 'district',
            'Bundesland': 'state',
            'Breitengrad': 'latitude',
            'Längengrad': 'longitude',
            'Inbetriebnahmedatum': 'commissioning_date',
            'Nennleistung Ladeeinrichtung [kW]': 'nominal_power',
            'Art der Ladeeinrichtung': 'charging_type',
            'Anzahl Ladepunkte': 'num_charging_points',
        }

        # Add dynamic socket fields
        for i in range(1, 7):
            rename_map[f'Steckertypen{i}'] = f'socket_type_{i}'
            rename_map[f'Nennleistung Stecker{i}'] = f'power_output_{i}'
            rename_map[f'Public Key{i}'] = f'public_key_{i}'

        # Rename columns in the dataframe
        df = df.rename(columns=rename_map)
        df = df.replace(["nan", "NaN", np.nan], None)

        result = []
        for idx, row in df.iterrows():
            row['geometry'] = Point(float(str(row['longitude']).replace(',', '.')),
                                    float(str(row['latitude']).replace(',', '.')))
            del row["longitude"]
            del row["latitude"]

            row["num_charging_points"] = int(row["num_charging_points"])
            row["commissioning_date"] = row['commissioning_date'].date()

            for i in range(1, 7):
                value_power_output = row[f'power_output_{i}']
                if value_power_output is not None and ";" in value_power_output:
                    row[f'power_output_{i}'] = float(value_power_output.split(";")[0])

            row["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(row["geometry"])
            row["data_source"] = context.resource.data_source
            row["data_acquisition_date"] = creation_date
            result.append(row)
        return result

    def _extract_ladesaeulen_data(self, filepath: str):
        # Load all rows including header info
        df_raw = pd.read_excel(filepath, header=None)

        # 1. Extract the update date from rows above the table
        update_date = None
        for row in df_raw[0]:
            if isinstance(row, str) and "Letzte Aktualisierung vom" in row:
                match = re.search(r"(\d{2}\.\d{2}\.\d{4})", row)
                if match:
                    update_date = match.group(1)
                break

        # 2. Read the actual table (starts at row 11 -> index 10)
        df_table = pd.read_excel(filepath, skiprows=10)

        return df_table, update_date
    
    def _safe_parse_list(s: str):
        fallback = ['Kreisfreie Stadt Kaiserslautern', 'Landkreis Kaiserslautern']
        try:
            result = ast.literal_eval(s)
            if isinstance(result, list):
                return [str(item) for item in result]
            return fallback
        except Exception:
            return fallback
