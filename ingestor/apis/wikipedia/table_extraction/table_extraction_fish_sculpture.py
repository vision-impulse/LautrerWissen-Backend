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

from ingestor.apis.wikipedia.table_extraction.table_extraction import WikipediaTableExtractor, WikipediaTableCellType


class FishSculptureTableExtractor(WikipediaTableExtractor):

    def __init__(self):
        table_structure = [("image", WikipediaTableCellType.IMAGE),
                           ("number", WikipediaTableCellType.TEXT),
                           ("name", WikipediaTableCellType.TEXT),
                           ("designed_by", WikipediaTableCellType.TEXT),
                           ("address_past", WikipediaTableCellType.TEXT),
                           ("address_name", WikipediaTableCellType.TEXT),
                           ("address", WikipediaTableCellType.ADDRESS)]
        super(FishSculptureTableExtractor, self).__init__(table_structure)
        self.geo_keyword = "Map"
        self.location_and_gps_originate_from_one_cell = False

    def extract_coords_from_url_string(self, input_string):
        pattern = r'/(\d+\.\d+)/(\d+\.\d+)/'
        match = re.search(pattern, input_string)

        if match:
            latitude = float(match.group(1))
            longitude = float(match.group(2))
            return (latitude, longitude)
        return None

    def apply_custom_transforms_data_frame(self, df):
        #df.replace({'number': {'': '1000'}}, inplace=True)
        #df['number'] = df['number'].astype(int)
        return df