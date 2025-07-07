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

import os.path

from ingestor.apis import Downloader
from ingestor.apis.wikipedia.page_extraction import WikipediaPageExtractor
from ingestor.apis.wikipedia.license_extraction import WikipediaLicenseExtractor
from ingestor.apis.wikipedia.wiki_dataframe import WikipediaDataframeColumns as WikiDFColumns
import re
import os
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import importlib
import time
import functools
import requests

TABLE_EXTRACTION_MODULE = 'ingestor.apis.wikipedia.table_extraction'

def polite_request(func):
    """
    Decorator that:
    - Sleeps 1 second before executing the request.
    - On 429 error, retries with increasing sleep intervals: 10s, then 60s, then exit.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        time.sleep(1)
        delays = [0, 10, 60]
        for i, delay in enumerate(delays):
            if delay > 0:
                print(f"Sleeping for {delay} seconds before retrying...")
                time.sleep(delay)

            try:
                response = func(*args, **kwargs)
                if response.status_code == 429:
                    if i == len(delays) - 1:
                        print("Received 429 too many times, exiting.")
                        exit(1)
                    else:
                        print(f"Received 429 (attempt {i+1}/3), will retry.")
                        continue  # retry the next delay
                else:
                    return response  
            except requests.exceptions.RequestException as e:
                print(f"Request failed with error: {e}")
                exit(1)
    return wrapper


class WikipediaDownloader(Downloader):

    def __init__(self, out_dir, wiki_resource, logger):
        super().__init__(out_dir)
        self.wiki_page = wiki_resource
        self.logger = logger

    def _log_info(self, message):
        """Helper method to standardize logging."""
        self.logger.info(message, extra={'classname': self.__class__.__name__})

    def run_download(self):
        self._log_info("*" * 40 + "\nStart downloading data from Wikipedia...")
        self._process_wiki_page(self.wiki_page)
        self._log_info("Download finished successfully!\n" + "*" * 40)

    def _process_wiki_page(self, page):
        """Handles the download and extraction of a Wikipedia page."""
        soup = self._download_wikipedia_page_and_parse_as_soup(page)

        references = WikipediaPageExtractor.extract_references(soup)
        tables = WikipediaPageExtractor.get_html_tables_for_wikipedia_page(soup)
        self._log_info(f"Found {len(tables)} tables on wikipage.")

        for idx, filename, extractor_name in zip(page.table_indices, page.table_filenames, page.table_extractor_classes):
            self._extract_and_save_table(extractor_name, tables[idx], filename, references)

    def _extract_and_save_table(self, extractor_name, html_table, filename, references):
        """Extracts, processes, and saves a table to a CSV file."""
        df_main = self._extract_table(extractor_name, html_table)

        df_license = self._download_image_licenses(df_main)
        df_additional_images = self._download_additional_images(df_main)
        df_combined = pd.concat([df_main, df_license, df_additional_images], axis=1)

        df_final = self._replace_and_add_references_to_dataframe(df_combined, references)
        df_final.to_csv(os.path.join(self.out_dir, filename), sep=";", encoding="utf-8")

    def _extract_table(self, extractor_name, html_table):
        """Extracts table from HTML and returns DataFrame."""
        self._log_info("Start table extraction...")
        ext_module = importlib.import_module(TABLE_EXTRACTION_MODULE)
        tbl_ext_class = getattr(ext_module, extractor_name)
        df = tbl_ext_class().extract_table(html_table)
        self._log_info("Table extraction finished successfully.")
        return df

    def _download_image_licenses(self, df):
        """Downloads and adds license information for images."""
        self._log_info("Downloading license info for extracted images...")
        df_license = pd.DataFrame(index=df.index,
                                  columns=[WikiDFColumns.IMAGE_AUTHOR_NAME.value,
                                           WikiDFColumns.IMAGE_LICENSE_URL.value,
                                           WikiDFColumns.IMAGE_LICENSE_TEXT.value])

        relevant_rows = df[df[WikiDFColumns.IMAGE_FILENAME.value] != ""]
        for index in tqdm(relevant_rows.index, desc="Downloading image license information"):
            image_file_name = df.at[index, WikiDFColumns.IMAGE_FILENAME.value]
            user, license_url, license_text = self._download_license_info_for_image_name(image_file_name)
            df_license.at[index, WikiDFColumns.IMAGE_AUTHOR_NAME.value] = user
            df_license.at[index, WikiDFColumns.IMAGE_LICENSE_URL.value] = license_url
            df_license.at[index, WikiDFColumns.IMAGE_LICENSE_TEXT.value] = license_text

        self._log_info("Successfully downloaded license info from extracted images.")
        return df_license

    def _download_additional_images(self, df):
        """Downloads additional images via category pages."""
        self._log_info("Downloading additional images and license info via category pages...")
        df_additional = pd.DataFrame(index=df.index,
                                     columns=[WikiDFColumns.ADDITIONAL_IMAGE_URLS.value,
                                              WikiDFColumns.ADDITIONAL_IMAGE_AUTHOR_NAMES.value,
                                              WikiDFColumns.ADDITIONAL_IMAGE_LICENSE_URLS.value,
                                              WikiDFColumns.ADDITIONAL_IMAGE_LICENSE_TEXTS.value]
                                     ).astype(str)

        relevant_rows = df[df[WikiDFColumns.ADDITIONAL_IMAGE_URL_CATEGORY.value] != ""]
        for index in tqdm(relevant_rows.index, desc="Downloading additional images"):
            category_url = df.at[index, WikiDFColumns.ADDITIONAL_IMAGE_URL_CATEGORY.value]
            """
            image_urls = self.get_additional_image_links(category_url)
            for image_url in image_urls[:2]:
                image_file_name = image_url.split("px-")[-1]  # Extract image name from URL
                user, license_url, license_text = self.get_additional_image_links(image_file_name)
                df_additional.at[index, WikiDFColumns.ADDITIONAL_IMAGE_URLS.value] += image_url + ";"
                df_additional.at[index, WikiDFColumns.ADDITIONAL_IMAGE_AUTHOR_NAMES.value] += user + ";"
                df_additional.at[index, WikiDFColumns.ADDITIONAL_IMAGE_LICENSE_URLS.value] += license_url + ";"
                df_additional.at[index, WikiDFColumns.ADDITIONAL_IMAGE_LICENSE_TEXTS.value] += license_text + ";"
            """

        self._log_info("Successfully downloaded additional images and license info.")
        return df_additional

    def _replace_and_add_references_to_dataframe(self, df, references):
        """Extracts and adds references to all string columns in the DataFrame."""
        self._log_info("Extracting references...")

        df_refs = df.copy()  # Copy original DataFrame
        df_refs[[WikiDFColumns.REFERENCE_NAMES.value, WikiDFColumns.REFERENCE_LINKS.value]] = '' # Add reference columns

        for row_index, row in df_refs.iterrows():
            for col_index, col_name in enumerate(df.columns):
                if not isinstance(row[col_name], str):  # Only process string columns
                    continue

                ref_matches = re.findall(r'\[\d+\]', row[col_name])  # Find reference numbers

                for ref_idx, ref in enumerate(ref_matches):
                    ref_num = int(ref[1:-1]) - 1  # Convert '[1]' → 0-based index
                    ref_info = references[ref_num]

                    # Replace reference in the cell text
                    df_refs.at[row_index, col_name] = row[col_name].replace(ref, f"[{ref_idx + 1}]")

                    # Append extracted reference details
                    df_refs.at[row_index, WikiDFColumns.REFERENCE_NAMES.value] += ref_info[0] + ";"
                    df_refs.at[row_index, WikiDFColumns.REFERENCE_LINKS.value] += ref_info[1] + ";"

        self._log_info("Successfully extracted references.")
        return df_refs

    def _download_wikipedia_page_and_parse_as_soup(self, page):
        self._log_info(f"Downloading wikipage ({page.page_name}) from Wikipedia...")
        html = self._get_wikipedia_page_html(page.page_name)
        soup = BeautifulSoup(html, 'html.parser')
        self._log_info("Successfully downloaded and parsed wiki page.")
        return soup

    @staticmethod
    def _get_wikipedia_page_html(page_name):
        response = WikipediaDownloader._download_main_wikipage(page_name)
        print(response)
        return response.json()['parse']['text']['*']

    @staticmethod
    def _download_license_info_for_image_name(image_name):
        """Fetch license info for an image."""
        response = WikipediaDownloader._download_license_page_with_image_info(image_name)
        soup = BeautifulSoup(response.content, 'html.parser')
        return WikipediaLicenseExtractor.extract_user_and_licence_from_image(soup)

    @staticmethod
    def get_additional_image_links(url):
        """Scrape additional image URLs from a category page."""
        response = WikipediaDownloader._download_category_page_with_image_links(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        image_links = []
        for gallerybox in soup.find_all("li", class_="gallerybox"):
            img_tag = gallerybox.find("img")
            if img_tag and img_tag.has_attr("src"):
                image_links.append(img_tag["src"])
        return image_links
    
    # ----------------------------------------------------------------------------------------------------------------

    @staticmethod
    @polite_request
    def _download_main_wikipage(page_name):
        """Fetch raw Wikipedia HTML."""
        params = {
            "action": "parse",
            "format": "json",
            "page": page_name,
            "prop": "text",
        }
        url = "https://de.wikipedia.org/w/api.php"
        print("Making wiki request", url)
        response = requests.get(url, params=params)
        return response

    @staticmethod
    @polite_request
    def _download_category_page_with_image_links(url):
        print("Making wiki request", url)
        response = requests.get(url)
        return response

    @staticmethod
    @polite_request
    def _download_license_page_with_image_info(image_name):
        url = "https://commons.wikimedia.org/wiki/File:" + image_name
        print("Making wiki request", url)
        response = requests.get(url)
        return response

