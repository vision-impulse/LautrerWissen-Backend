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
import pandas as pd
import requests
import datetime

from ingestor.apis import Downloader
from ingestor.config.env_config import WASGEHTAPP_PASS
from ingestor.config.env_config import WASGEHTAPP_USER


class WGAEventDownloader(Downloader):

    HEADERS = {
        "User-Agent": "Wasgehtapp-Importer-KL",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    NUM_MONTHS = 12

    def __init__(self, out_dir, wga_event_resource, logger):
        super(WGAEventDownloader, self).__init__(out_dir)
        self.out_fp = os.path.join(out_dir, wga_event_resource.filename)
        self.logger = logger
        self.url = wga_event_resource.url
        self.wga_event_resource = wga_event_resource

    def perform_download(self):
        data = []
        for i in range(WGAEventDownloader.NUM_MONTHS):
            datum_start = (datetime.date.today() + datetime.timedelta(days=31*i)).strftime("%Y-%m-%d")
            datum_end = (datetime.date.today() + datetime.timedelta(days=31*(i+1))).strftime("%Y-%m-%d")
            self.logger.info("Downloading events between %s and %s", datum_start, datum_end)
            _data = self._fetch_data_from_api(datum_start, datum_end)
            data.extend(_data)

        df = pd.DataFrame(data)
        df = df.reset_index()
        df.to_csv(self.out_fp, sep=";", encoding="utf-8")

    def _fetch_data_from_api(self, datum_start, datum_end):
        payload = {
            "mail": WASGEHTAPP_USER,
            "passwort": WASGEHTAPP_PASS,
            "columns": "subtitel,beschreibung,ort,plz,strasse,location_url,location_bild,location_id,"
                       "sublocation,lat,lng,url,youtube,groupid",
            "datum_start": datum_start,
            "datum_ende": datum_end,
            "lat": self.wga_event_resource.region_latitude,
            "lng": self.wga_event_resource.region_longitude,
            "radius": self.wga_event_resource.region_region,

        }
        response = requests.post(self.url, headers=WGAEventDownloader.HEADERS, data=payload)
        if response.status_code == 200:
            termine = response.json()
            self.logger.info("Read data (%s events)", len(termine))
            return termine["data"]
        else:
            self.logger.error("Error (Code: %s) %s", response.status_code, response.text)
        return []
