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


class MiadiEventsTransformStep(DefaultTransformStep):

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        result = []

        df = pd.read_csv(download_file, sep=";")
        df = df.drop(columns=['Unnamed: 0', 'index'])
        rows_as_dict = df.to_dict(orient='records')
        for row in rows_as_dict:
            row["event_id"] = row["id"]
            row["dstart"] = datetime.strptime(row["dstart"], '%d.%m.%Y %H:%M:%S')
            row["dend"] = datetime.strptime(row["dend"], '%d.%m.%Y %H:%M:%S')
            row["created"] = datetime.strptime(row["created"], '%d.%m.%Y %H:%M:%S')
            row["updated"] = datetime.strptime(row["updated"], '%d.%m.%Y %H:%M:%S')
            row = {k: self._clean_nan(v) for k, v in row.items()}

            row["city_district_name"] = ""  # check
            row["data_source"] = context.resource.data_source
            row["data_acquisition_date"] = data_acquisition_date
            result.append(row)
        return result

    def _clean_nan(self, value):
        return None if pd.isna(value) else value

