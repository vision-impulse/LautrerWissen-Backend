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

import requests
from ingestor.datapipe.steps.base_step import PipelineStep
from ingestor.apis.osm.osm import OSMDownloader
from ingestor.apis.wga.wga_api import WGAEventDownloader
from ingestor.apis.wfs.wfs import WFSDownloader
from ingestor.apis.miadi.event_calendar import EventCalendarDownloader
from ingestor.apis.ris.council_calendar import CouncilCalendarDownloader
from ingestor.apis.wikipedia.wiki_downloader import WikipediaDownloader
from ingestor.apis.mqtt.mqtt_static_sensors import MQTTInitialSensorsDownloader
from ingestor.apis import ResourceDownloader, LocalResourceDownloader
from typing import Type, Dict
import traceback


class GenericDownloadStep(PipelineStep):

    def __init__(self, downloader_class):
        super(GenericDownloadStep, self).__init__(next_step=None)
        self.downloader_class = downloader_class

    def execute(self, context):
        print(f"Downloading {context.resource} to ...") #{context.resource.filename}
        try:
            self.downloader_class(context.out_dir, context.resource, context.logger).run_download()
            return True
        except Exception as e:
            traceback.print_exc()
            print(f"Download failed for {context.resource}: {e}")
            return False


class DownloadStepFactory:
    """Factory for creating download steps dynamically based on the downloader class."""

    _registry: Dict[Type, GenericDownloadStep] = {}  # Stores {DownloaderClass: GenericDownloadStep}

    @classmethod
    def register(cls, downloader_class: Type):
        """Registers a downloader class."""
        cls._registry[downloader_class] = GenericDownloadStep(downloader_class)

    @classmethod
    def create(cls, downloader_class: Type):
        """Creates a `GenericDownloadStep` for the given `downloader_class`."""
        if downloader_class not in cls._registry:
            raise ValueError(f"No download step registered for {downloader_class.__name__}")
        return cls._registry[downloader_class]


# Register All Available Downloaders
DownloadStepFactory.register(WikipediaDownloader)
DownloadStepFactory.register(OSMDownloader)
DownloadStepFactory.register(EventCalendarDownloader)
DownloadStepFactory.register(CouncilCalendarDownloader)
DownloadStepFactory.register(WFSDownloader)
DownloadStepFactory.register(ResourceDownloader)
DownloadStepFactory.register(LocalResourceDownloader)
DownloadStepFactory.register(WGAEventDownloader)
DownloadStepFactory.register(MQTTInitialSensorsDownloader)





