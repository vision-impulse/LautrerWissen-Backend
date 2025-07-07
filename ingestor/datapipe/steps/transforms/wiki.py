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

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from datetime import datetime
import os

from ingestor.apis.wikipedia.wiki_dataframe import WikipediaDataframeColumns as WikiDFColumns
from ingestor.utils.geo_districts import CityDistrictsDecoder


class WikiTransformStep(DefaultTransformStep):

    def transform(self, context, db_model, data_acquisition_date):

        result = []
        for fn in context.resource.table_filenames:
            download_file = os.path.join(context.out_dir, fn)
            print("processing", download_file)
            df = pd.read_csv(download_file, sep=";")
            df = df.fillna("")

            df[WikiDFColumns.ADDRESS_LOCATION.value] = \
                df[WikiDFColumns.ADDRESS_LOCATION.value].apply(lambda x: tuple(map(float, x.strip('()').split(','))))
            df = df.drop(columns=['Unnamed: 0', ])

            rows_as_dict = df.to_dict(orient='records')
            for row in rows_as_dict:
                loc = tuple(list(row[WikiDFColumns.ADDRESS_LOCATION.value]))
                row["geometry"] = Point(loc[1], loc[0])  # lng, lat

                if context.resource.table_filenames[0] == "wiki_fish_sculptures.csv":
                    row["address"] = row["address_name"]
                    del row["address_name"]
                    if row["number"] == "":
                        row["number"] = -1
                else:
                    row["address"] = row[WikiDFColumns.ADDRESS_TEXT.value]# "loc_address_text"

                del row["id"]
                del row[WikiDFColumns.ADDRESS_TEXT.value]
                del row[WikiDFColumns.ADDRESS_LOCATION.value]
                del row[WikiDFColumns.IMAGE_FILENAME.value]
                del row[WikiDFColumns.ADDITIONAL_IMAGE_URL_CATEGORY.value]

                row["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(row["geometry"])
                row["data_source"] = context.resource.data_source
                row["data_acquisition_date"] = data_acquisition_date

                result.append(row)
        return result
