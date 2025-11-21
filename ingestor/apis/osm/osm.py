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

class OSMDownloader(Downloader):

    def __init__(self, out_dir, osm_resource, logger):
        super(OSMDownloader, self).__init__(out_dir)
        self.osm_resource = osm_resource
        self.logger = logger

    def perform_download(self):
        tag_type = self.osm_resource.tags
        output_file = self.osm_resource.filename
        try:
            self._on_resource_download_start(tag_type)
            gdf = ox.features_from_place(self.osm_resource.place_filter, tag_type)
            out_path = os.path.join(self.out_dir, "%s" % (output_file))
            gdf.to_file(out_path, driver="GeoJSON", engine="pyogrio")
            self._on_resource_downloaded(self.out_dir, output_file)
        except Exception as err:
            self._on_resource_error(tag_type, err)

    def _on_resource_download_start(self, tag_type):
        self.logger.info("Start resource download from OSM for tags (%s)" %(tag_type),
                         extra={'classname': self.__class__.__name__})

    def _on_resource_error(self, tags, err):
        self.logger.error("Error occurred while downloading the file from OSM for %s!" % (tags),
                          extra={'classname': self.__class__.__name__})
        self.logger.error(err, extra={'classname': self.__class__.__name__})

