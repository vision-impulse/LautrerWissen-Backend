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
from datetime import datetime
import pandas as pd
import os


class WGAEventTransformStep(DefaultTransformStep):

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        result = []

        df = pd.read_csv(download_file, sep=";")
        df = df.drop_duplicates(subset='id', keep='first')
        df = df.rename(columns={
            'id': 'event_id',
            'titel': 'title',
            'datum': 'date',
            'zeit': 'time',
            'kategorie': 'category',
            'subtitel': 'subtitle',
            'beschreibung': 'description',
            'ort': 'city',
            'plz': 'postal_code',
            'strasse': 'street',
            'location_bild': 'location_image',
            'lat': 'latitude',
            'lng': 'longitude',
            'url': 'event_url',
            'youtube': 'youtube_video',
            'groupid': 'group_id',
            'datum_iso': 'date_iso',
        })
        df = df.drop_duplicates(subset='event_id', keep='first')

        df = df.drop(columns=['Unnamed: 0', 'index'])
        rows_as_dict = df.to_dict(orient='records')
        for row in rows_as_dict:
            row["date"] = datetime.strptime(row["date"], '%d.%m.%Y').date()
            row["city_district_name"] = ""  # check
            row["data_source"] = context.resource.data_source
            row["data_acquisition_date"] = data_acquisition_date
            result.append(row)
        return result
