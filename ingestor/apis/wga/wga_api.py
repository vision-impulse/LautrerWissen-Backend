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
import pandas as pd
import requests
import datetime

WASGEHTAPP_USER = os.getenv('WASGEHTAPP_USER')
WASGEHTAPP_PASS = os.getenv('WASGEHTAPP_PASS')

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
            "lat": 49.4454858,
            "lng": 7.7581375,
            "radius": 30,
        }
        response = requests.post(self.url, headers=WGAEventDownloader.HEADERS, data=payload)
        if response.status_code == 200:
            termine = response.json()
            self.logger.info("Read data (%s events)", len(termine))
            return termine["data"]
        else:
            self.logger.error("Error (Code: %s) %s", response.status_code, response.text)
        return []
