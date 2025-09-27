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

from ingestor.apis import LocalResourceDownloader
from ..steps.download.step_download import DownloadStepFactory
from ..steps.transforms.wifi import WifiTransformStep
from ..steps.geo.step_filter import FilterStep
from ..steps.database.step_import import GenericImportStep
from ..pipelines.base_pipeline import BasePipeline, PipelineType


class WifiMySpotEmperaPipeline(BasePipeline):
    """Pipeline for Wifi data (Empera and MySpot)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_pipeline(self):
        return [
            DownloadStepFactory.create(LocalResourceDownloader),
            WifiTransformStep(),
            GenericImportStep(),
        ]
