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

import pandas as pd
import re
from bs4 import BeautifulSoup
from ingestor.apis.wikipedia.wiki_dataframe import WikipediaDataframeColumns as WikiDfColums

from enum import Enum


class WikipediaTableCellType(Enum):
    TEXT = "Text"
    ADDRESS = "Address"
    IMAGE = "Image"
    IGNORE = "Ignore"


def normalize_table(table):
    """Modifies an HTML table to explicitly repeat rowspan content in following rows."""

    rows = table.find_all('tr')  # Extract all rows
    rowspan_tracker = {}  # Dictionary to track rowspan content (column index -> (cell, remaining_span))

    normalized_rows = []  # Store modified rows

    for row_idx, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        new_cells = []
        col_idx = 0  # Track column index manually (includes rowspan inserts)

        for cell in cells:
            # Insert any pending rowspan cells before handling the new cell
            while col_idx in rowspan_tracker:
                stored_cell, remaining_span = rowspan_tracker[col_idx]
                new_cell = BeautifulSoup(str(stored_cell), 'html.parser').td  # Duplicate the tag
                new_cells.append(new_cell)  # Append the repeated cell
                rowspan_tracker[col_idx] = (stored_cell, remaining_span - 1)  # Decrease rowspan count

                # Remove from tracker if span is finished
                if rowspan_tracker[col_idx][1] == 0:
                    del rowspan_tracker[col_idx]

                col_idx += 1  # Move to next column

            # Now handle the current actual cell
            rowspan = int(cell.get('rowspan', 1))  # Extract rowspan value
            if rowspan > 1:
                # Store cell for future rows if rowspan exists
                rowspan_tracker[col_idx] = (cell, rowspan - 1)

            new_cells.append(cell)
            col_idx += 1  # Move to next column

        # Fill remaining columns with any missing rowspan content
        while col_idx in rowspan_tracker:
            stored_cell, remaining_span = rowspan_tracker[col_idx]
            new_cell = BeautifulSoup(str(stored_cell), 'html.parser').td
            new_cells.append(new_cell)
            rowspan_tracker[col_idx] = (stored_cell, remaining_span - 1)

            if rowspan_tracker[col_idx][1] == 0:
                del rowspan_tracker[col_idx]

            col_idx += 1

        # Replace original row's content with modified cells
        row.clear()
        for cell in new_cells:
            row.append(cell)

        normalized_rows.append(row)

    return table  # Return modified table



class WikipediaTableExtractor(object):

    def __init__(self, table_structure):
        self.table_structure = table_structure
        self.geo_keyword = None
        self.location_and_gps_originate_from_one_cell = True

    def extract_table(self, html_table):
        table_data = self._extract_table_from_html(html_table)
        df_table = self._create_data_frame(table_data)
        df_table = self.apply_custom_transforms_data_frame(df_table)
        print("Table extraction completed...")
        return df_table

    def extract_coords_from_url_string(self, input_string):
        raise NotImplementedError

    def apply_custom_transforms_data_frame(self, df):
        return df

    def _extract_table_from_html(self, html_table):
        table_data = []

        # Print parsed table for debugging
        table = normalize_table(html_table)
        #print(html_table.prettify())

        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) != len(self.table_structure):
                print("im if", "colspan", row)
                continue

            address_found_in_row, row_data = self._extract_single_row(row)
            if address_found_in_row:
                table_data.append(row_data)
        return table_data

    def _extract_single_row(self, row):
        address_found_in_row = False
        row_data = []
        cells = row.find_all(['td', 'th'])

        for idx, cell_info in enumerate(self.table_structure):
            name, cell_data_type = cell_info
            cell = cells[idx]
            if cell_data_type == WikipediaTableCellType.IGNORE:
                continue
            elif cell_data_type == WikipediaTableCellType.ADDRESS:
                data, address_found_in_row = self._extract_address_content(cell)
            elif cell_data_type == WikipediaTableCellType.TEXT:
                data = WikipediaTableExtractor._extract_text_content(cell)
            elif cell_data_type == WikipediaTableCellType.IMAGE:
                data = WikipediaTableExtractor._extract_image_content(cell)

            row_data += data
        return address_found_in_row, row_data

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
                        row_data.append(cell_text[:-4].strip())  # split location and gps in two separate columns
                    else:
                        row_data.append(None)

                    gps = self.extract_coords_from_url_string(link['href'])
                    cell_text = gps
                    address_found_in_row = True
                    break
        row_data.append(cell_text)
        return row_data, address_found_in_row

    @staticmethod
    def _extract_text_content(cell):
        text = []
        for element in cell.children:
            if element.name == 'div':
                text.append(element.get_text())
            if element.name == 'a':
                text.append(element.get_text())
            elif element.name == 'sup':
                sup_text = element.get_text(strip=True)
                text.append(sup_text)  # Format as [number]
            elif element.string:  # If it's a string
                text.append(element.string.strip())  # Append the text without leading/trailing whitespace

        cell_text = ' '.join(text).replace('  ', ' ').strip()
        return [cell_text, ]

    @staticmethod
    def _extract_image_content(cell):
        image_available = False
        row_info = {WikiDfColums.IMAGE_URL: "",
                    WikiDfColums.IMAGE_FILENAME: "",
                    WikiDfColums.ADDITIONAL_IMAGE_URL_CATEGORY: ""}
        cell_text = ""
        imgs = cell.findAll('img')
        if len(imgs) > 0:  # is an image cell
            for img in imgs:
                if "maps.wikimedia" in img["src"]:
                    continue

                cell_text = "https:" + img["src"]  # select first image
                row_info[WikiDfColums.IMAGE_URL] = cell_text

                for a in cell.findAll('a'):
                    if 'class' in a.attrs and 'mw-file-description' in a["class"]:
                        cell_text = a["href"].replace("/wiki/Datei:", "")  # image_file_name
                        row_info[WikiDfColums.IMAGE_FILENAME] = cell_text
                        image_available = True
                    if 'class' in a.attrs and 'extiw' in a["class"] and a.text == "weitere Bilder":
                        row_info[WikiDfColums.ADDITIONAL_IMAGE_URL_CATEGORY] = a["href"]
                        print("WEITERE BILDER VERFÜGBAR")
                if not image_available:
                    cell_text = ""
        else:
            return ["", "", ""]

        if "Missing_image_icon_with_camera_and_upload_arrow.svg.png" in row_info[WikiDfColums.IMAGE_URL]:
            row_info[WikiDfColums.IMAGE_URL] = ""

        if str(row_info[WikiDfColums.IMAGE_URL]) in ("NaN", "nan"):
            row_info[WikiDfColums.IMAGE_URL] = ""

        return row_info[WikiDfColums.IMAGE_URL], row_info[WikiDfColums.IMAGE_FILENAME], \
               row_info[WikiDfColums.ADDITIONAL_IMAGE_URL_CATEGORY]

    def _create_data_frame(self, table_data):
        df = pd.DataFrame(table_data)
        df = df.reset_index()
        df.rename(columns={'index': 'id'}, inplace=True)
        cols = self._create_colum_names()
        df.columns = cols
        return df

    def _create_colum_names(self):
        col_names = ['id', ]
        for col_name, col_type in self.table_structure:
            if col_type == WikipediaTableCellType.IGNORE:
                continue
            if col_type == WikipediaTableCellType.TEXT:
                col_names.append(col_name)
            elif col_type == WikipediaTableCellType.IMAGE:
                col_names.extend([WikiDfColums.IMAGE_URL.value,
                                  WikiDfColums.IMAGE_FILENAME.value,
                                  WikiDfColums.ADDITIONAL_IMAGE_URL_CATEGORY.value])
            elif col_type == WikipediaTableCellType.ADDRESS:
                col_names.extend([WikiDfColums.ADDRESS_TEXT.value, WikiDfColums.ADDRESS_LOCATION.value])
        return col_names


class DefaultWikipediaTableExtractor(WikipediaTableExtractor):

    def __init__(self, table_structure):
        super(DefaultWikipediaTableExtractor, self).__init__(table_structure)
        self.geo_keyword = "geohack"
        self.location_and_gps_originate_from_one_cell = True

    def extract_coords_from_url_string(self, input_string):
        coord_string = DefaultWikipediaTableExtractor._extract_gps_from_wikipedia_link(input_string)
        if coord_string is None:
            return None
        return DefaultWikipediaTableExtractor._convert_coord_str_to_gps(coord_string)

    @staticmethod
    def _extract_gps_from_wikipedia_link(url):
        pattern = r'params=([\d\.\_NSEW]+)'
        match = re.search(pattern, url)
        coords = None
        if match:
            coords = match.group(1)
        return coords

    @staticmethod
    def _convert_coord_str_to_gps(coord_string):
        # coord_string = "49.445175_N_7.785199_E"

        # Split the string into latitude and longitude
        parts = coord_string.split('_')

        lat_str = parts[0] + '_' + parts[1]  # e.g., "49.445175_N"
        lon_str = parts[2] + '_' + parts[3]  # e.g., "7.785199_E"

        # Convert latitude to float
        if lat_str.endswith('N'):
            latitude = float(lat_str[:-2])
        elif lat_str.endswith('S'):
            latitude = -float(lat_str[:-2])

        # Convert longitude to float
        if lon_str.endswith('E'):
            longitude = float(lon_str[:-2])
        elif lon_str.endswith('W'):
            longitude = -float(lon_str[:-2])

        # Create the tuple
        coords_tuple = (latitude, longitude)
        return coords_tuple

