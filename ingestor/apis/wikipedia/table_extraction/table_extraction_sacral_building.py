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

from ingestor.apis.wikipedia.table_extraction.table_extraction import DefaultWikipediaTableExtractor, WikipediaTableCellType


class SacralBuildingsTableExtractor(DefaultWikipediaTableExtractor):

    def __init__(self):
        table_structure = [("image", WikipediaTableCellType.IMAGE),
                           ("image_inside", WikipediaTableCellType.IGNORE),
                           ("name", WikipediaTableCellType.TEXT),
                           ("address", WikipediaTableCellType.ADDRESS),
                           ("construction_year", WikipediaTableCellType.TEXT),
                           ("description", WikipediaTableCellType.TEXT), ]
        super(SacralBuildingsTableExtractor, self).__init__(table_structure)


    def _extract_address_content(self, cell):
        address_found_in_row = False
        cell_text = " ".join(cell.stripped_strings)
        cell_text = cell_text.replace(" ,", ",")
        row_data = []
        links = cell.findAll('a')

        for link in links:
            if link and 'href' in link.attrs:
                if self.geo_keyword in link['href']:
                    if self.location_and_gps_originate_from_one_cell:
                        row_data.append(cell_text[:-12].strip())  # split location and gps in two separate columns
                    else:
                        row_data.append(None)

                    gps = self.extract_coords_from_url_string(link['href'])
                    cell_text = gps
                    address_found_in_row = True
                    break
        row_data.append(cell_text)
        return row_data, address_found_in_row