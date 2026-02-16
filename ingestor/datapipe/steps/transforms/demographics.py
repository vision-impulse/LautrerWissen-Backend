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
import json
import logging
import pandas as pd
import csv
import datetime
import os
import logging

from ingestor.datapipe.steps.base_step import DefaultTransformStep

logger = logging.getLogger(__name__)


class DemographicsTransformStep(DefaultTransformStep):

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
    
        if not os.path.exists(download_file):
            logger.error("File for data import not found: %s." % (download_file))
            return

        df_complete = self.read_df_from_csv(download_file)        
        df_complete['data_source'] = [context.resource.data_source for _ in range(len(df_complete))]
        df_complete['data_acquisition_date'] = [data_acquisition_date for _ in range(len(df_complete))]

        return df_complete.to_dict('records')
    
    def read_df_from_csv(self, csv_fp):
        try:
            csv_header_types = {'GebietsID': str, 'BisKleinerAls': str, 'von': str}
            df_raw = pd.read_csv(csv_fp, sep=';', encoding='latin1', dtype=csv_header_types)
        except UnicodeDecodeError:
            df_raw = pd.read_csv(csv_fp, sep=';', encoding='cp1252', dtype=csv_header_types)
        df_raw = df_raw.dropna(subset=['von', 'BisKleinerAls'])

        # Extract metadata encoded in rows and columns 
        meta_dict = {
            str(row['MetaSchlüssel']): [
                row['MetaWert01'] if pd.notna(row['MetaWert01']) else None,
                row['MetaWert02'] if pd.notna(row['MetaWert02']) else None
            ] 
            for _, row in df_raw.iterrows() 
            if pd.notna(row['MetaSchlüssel'])
        }

        # Convert date
        raw_date = meta_dict.get('Stichtag', [None])[0]
        current_reporting_date = pd.to_datetime(raw_date, dayfirst=True).strftime('%Y-%m-%d') if raw_date else None
        current_remark = meta_dict.get('allgemeiner Hinweis', [None])[0]

        # Define age groups
        df_raw['age_group'] = 'von ' + df_raw['von'].astype(str) + ' bis unter ' \
            + df_raw['BisKleinerAls'].astype(str)

        # Move 'Männlich' und 'Weiblich' in separate rows
        df_melted = df_raw.melt(
            id_vars=['GebietsID', 'Gebietsname', 'age_group'],
            value_vars=['Männlich', 'Weiblich'],
            var_name='gender',
            value_name='population_count'
        )

        df_final = pd.DataFrame({
            'city_district_id': df_melted['GebietsID'],
            'city_district_name': df_melted['Gebietsname'],
            'age_group': df_melted['age_group'],
            'gender': df_melted['gender'],
            'population_count': df_melted['population_count'],
            'reporting_date': current_reporting_date,
            'remark': current_remark
        })

        # Aggregate overall by gender and age group
        df_totals = df_final.groupby(['age_group', 'gender', 'reporting_date']).agg({
            'population_count': 'sum'
        }).reset_index()
        df_totals['city_district_id'] = '00'
        df_totals['city_district_name'] = "Gesamt Kaiserslautern"
        df_totals['remark'] = current_remark

        # Combine dataframes and add metadata as JSON
        df_complete = pd.concat([df_final, df_totals], ignore_index=True)
        df_complete['metadata'] = [meta_dict for _ in range(len(df_complete))]
        return df_complete