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


from ingestor.apis import ResourceDownloader
from ..steps.download.step_download import DownloadStepFactory
from ..steps.transforms.kl_geo import KLGeoResourceTransformStep
from ..steps.database.step_import import GenericImportStep
from ..pipelines.base_pipeline import BasePipeline, PipelineType


class KLGeoResourcePipeline(BasePipeline):
    """Pipeline for Geodata data."""

    def __init__(self, resources, out_dir, logger):
        super(KLGeoResourcePipeline, self).__init__(resources, logger, out_dir)

    def build_pipeline(self):
        return [DownloadStepFactory.create(ResourceDownloader),
                KLGeoResourceTransformStep(),
                GenericImportStep()]