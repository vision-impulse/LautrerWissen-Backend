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
import osmnx as ox
import requests
import pandas as pd
import geopandas as gpd
import shutil
from owslib.wfs import WebFeatureService
from io import BytesIO
from urllib.parse import urlparse


class Downloader(object):

    def __init__(self, out_dir, logger=None):
        super(Downloader, self).__init__()
        self.out_dir = out_dir
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        self.logger = logger

    def run_download(self):
        self.logger.info("*" * 40, extra={'classname': self.__class__.__name__})
        self.perform_download()
        self.logger.info("*" * 40, extra={'classname': self.__class__.__name__})

    def _on_resource_error(self, url, err):
        self.logger.error("Error occurred while downloading the file from %s!" % (url),
                          extra={'classname': self.__class__.__name__})
        self.logger.error(err, extra={'classname': self.__class__.__name__})

    def _on_resource_downloaded(self, out_dir, output_file):
        self.logger.info("Download completed successfully!",
                         extra={'classname': self.__class__.__name__})
        self.logger.info("File saved as %s " % (os.path.join(out_dir, output_file)),
                         extra={'classname': self.__class__.__name__})

    def perform_download(self):
        raise NotImplementedError


class XMLDownloader(Downloader):

    def __init__(self, out_dir, url, filename, logger):
        super(XMLDownloader, self).__init__(out_dir, logger)
        self.url = url
        self.filename = filename
        self.out_fp = os.path.join(self.out_dir, self.filename)

    def _parse_xml(self, response_content):
        raise NotImplementedError

    def perform_download(self):
        self.response = requests.get(self.url)

        items = self._parse_xml(self.response.content)

        df = pd.DataFrame(items)
        df = df.reset_index()
        df.to_csv(self.out_fp, sep=";", encoding="utf-8")


class ResourceDownloader(Downloader):

    def __init__(self, out_dir, resource_file, logger=None):
        super(ResourceDownloader, self).__init__(out_dir, logger)
        self.resource_file = resource_file

    def _on_resource_download_start(self, url):
        self.logger.info("Start resource download from %s" %(url), extra={'classname': self.__class__.__name__})

    def perform_download(self):
        local_path = self.resource_file.local_path
        if local_path and local_path.lower().startswith("file://"):
            self._copy_local_file()
            return

        url = self.resource_file.url
        if url:
            scheme = urlparse(url).scheme
            if scheme in ("http", "https"):
                self._download_file_resource()
                            

    def _download_file_resource(self):
        output_file = os.path.join(self.out_dir, self.resource_file.filename)
        url = self.resource_file.url
        self._on_resource_download_start(url)
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self._on_resource_downloaded(self.out_dir, output_file)
        else:
            self._on_resource_error(url, response.status_code)
            raise Exception("Error downloading the resource from %s" %(url))

    def _copy_local_file(self):
        dst = os.path.join(self.out_dir, self.resource_file.filename)

        data_folder = os.getenv("APP_DATA_DIR", "./data/") # Fallback    
        data_folder = os.path.join(data_folder, "init")
        src = os.path.join(data_folder, self.resource_file.filename)
        shutil.copy(src, dst)

    
