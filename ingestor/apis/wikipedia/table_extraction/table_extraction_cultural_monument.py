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
import re


class CulturalMonumentTableExtractor(DefaultWikipediaTableExtractor):

    def __init__(self):
        table_structure = [("name", WikipediaTableCellType.TEXT),
                           ("address", WikipediaTableCellType.ADDRESS),
                           ("construction_year", WikipediaTableCellType.TEXT),
                           ("description", WikipediaTableCellType.TEXT),
                           ("image", WikipediaTableCellType.IMAGE)]
        super(CulturalMonumentTableExtractor, self).__init__(table_structure)


class CulturalMonumentTableExtractor_Special(DefaultWikipediaTableExtractor):

    def __init__(self):
        table_structure = [("name", WikipediaTableCellType.TEXT),
                           ("address", WikipediaTableCellType.ADDRESS),
                           ("construction_year", WikipediaTableCellType.TEXT),
                           ("description", WikipediaTableCellType.TEXT),
                           ("image", WikipediaTableCellType.IMAGE)]
        super(CulturalMonumentTableExtractor_Special, self).__init__(table_structure)

    def _extract_table_from_html(self, html_table):
        table_data = []

        for row_idx, row in enumerate(html_table.find_all('tr')):
            # Note: the first row has a completely different format than the standard case. Locations are inside the
            # description, the location cell in the table is empty!
            if row_idx == 1:

                cells = row.find_all(['td', 'th'])
                name = " ".join(cells[0].stripped_strings).replace(" ,", ",")
                const_year = " ".join(cells[2].stripped_strings).replace(" ,", ",")

                desc = " ".join(cells[3].stripped_strings).replace(" ,", ",")
                desc = re.sub(r'\(([^()]*)\)', lambda x: f"({x.group(1).replace(',', '')})", desc) # replace "," in ()
                desc = desc.replace(");", "),") #
                description = ",".join([i for i in desc.split(",") if "(" not in i])

                image_url = ""
                image_available = False
                imgs = cells[4].findAll('img')
                if len(imgs) > 0:  # is an image cell
                    image_url = "https:" + imgs[0]["src"]  # select first image

                    for a in cells[4].findAll('a'):
                        if 'class' in a.attrs and 'mw-file-description' in a["class"]:
                            image_name = a["href"].replace("/wiki/Datei:", "")  # image_file_name
                            image_available = True
                            break
                    if not image_available:
                        image_name = ""

                locations = [i for i in desc.split(",") if "(" in i]
                for l in locations:
                    match_gps = re.search(r'\(\s*(?:[^⊙;]*;\s*)?⊙\s*([\d.]+)\s+([\d.]+)\s*\)', l)
                    if match_gps:
                        latitude = float(match_gps.group(1))
                        longitude = float(match_gps.group(2))
                        coordinates = (latitude, longitude)

                    match_address = re.match(r'^(.*\([^⊙;]*)(?:;|\s*⊙)', l)
                    if match_address:
                        address = match_address.group(1) + ")"
                        address = address.replace(" ( )", "")

                    if match_address and match_gps:
                        row_data = [name, address, coordinates, const_year, description, image_url, image_name, ""]
                        table_data.append(row_data)
            else:
                address_found_in_row, row_data = self._extract_single_row(row)
                if address_found_in_row:
                    table_data.append(row_data)
        return table_data
