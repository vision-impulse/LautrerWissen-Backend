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

from ingestor.apis import Downloader
import osmnx as ox
import os
import pandas as pd
import requests

import geopandas as gpd
from owslib.wfs import WebFeatureService
from requests import Request
from io import BytesIO


class WFSDownloader(Downloader):

    def __init__(self, out_dir, resource_wfs_file, logger=None):
        super(WFSDownloader, self).__init__(out_dir, logger)
        self.resource_wfs_file = resource_wfs_file

    def perform_download(self):
        resource_wfs_file = self.resource_wfs_file
        params = {
            "SERVICE": "WFS",
            "VERSION": "2.0.0",
            "REQUEST": "GetFeature",
            "TYPENAME": resource_wfs_file.layer_name,
            "SRSNAME": resource_wfs_file.srs_name,
            "OUTPUTFORMAT": resource_wfs_file.out_format
        }
        try:
            self._on_resource_download_start(resource_wfs_file.url, resource_wfs_file.filename)
            response = requests.get(resource_wfs_file.url, params=params)
            if response.status_code == 200:
                gdf = gpd.read_file(BytesIO(response.content))
                geojson_data = gdf.to_json()
                with open(os.path.join(self.out_dir, resource_wfs_file.filename), "w") as geojson_file:
                    geojson_file.write(geojson_data)
                self._on_resource_downloaded(self.out_dir, resource_wfs_file.filename)
            else:
                self._on_resource_error(resource_wfs_file.url, response.status_code)
        except Exception as err:
            self._on_resource_error(resource_wfs_file.url, err)

    def _on_resource_download_start(self, fn, url):
        self.logger.info("Start wfs download of layer %s from %s" %(fn, url),
                         extra={'classname': self.__class__.__name__})



