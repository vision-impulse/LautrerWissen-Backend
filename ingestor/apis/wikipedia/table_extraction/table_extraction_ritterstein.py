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


class RittersteinTableExtractor(DefaultWikipediaTableExtractor):

    def __init__(self):
        table_structure = [("number", WikipediaTableCellType.TEXT),
                           ("name", WikipediaTableCellType.TEXT),
                           ("meaning", WikipediaTableCellType.TEXT),
                           ("location_desc", WikipediaTableCellType.ADDRESS),
                           ("image", WikipediaTableCellType.IMAGE)]
        super(RittersteinTableExtractor, self).__init__(table_structure)

    def _extract_address_content(self, cell):
        address_found_in_row = False
        links = cell.findAll('a')
        gps = ""
        for link in links:
            if link and 'href' in link.attrs:
                if self.geo_keyword in link['href']:
                    gps = self.extract_coords_from_url_string(link['href'])
                    address_found_in_row = True
                    break

        for span in cell.find_all("span", class_="geo"):
            span.extract()

            # Get text with proper spacing for <a> tags
        for a in cell.find_all('a'):
            a.insert_before(' ')  # Ensure space before links

        location = cell.get_text(strip=True)

        # Remove any leading punctuation like ". "
        location = location.replace("⊙", "")
        if location.startswith(". "):
            location = location[2:]

        return [location, gps], address_found_in_row
