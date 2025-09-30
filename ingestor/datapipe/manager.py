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

import logging

from ingestor.datapipe.factory import PipelineFactory
from ingestor.utils.logging_utils import setup_logging

setup_logging()


class PipelineManager:
    """Manages multiple data pipelines."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def run_pipeline(self, source_name, resources, out_dir, run_record=None):
        pipeline = PipelineFactory.create_pipeline(
            source_name, resources, out_dir, self.logger, run_record
        )
        self.logger.info("Starting pipeline for data source: %s", source_name)
        result = pipeline.run()
        self.logger.info(
            "Pipeline for data source (%s) finished with result: %s",
            source_name,
            result,
        )
        return result
