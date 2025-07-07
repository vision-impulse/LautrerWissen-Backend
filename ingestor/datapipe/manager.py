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


from ingestor.datapipe.factory import PipelineFactory


class PipelineManager:
    """Manages multiple data pipelines."""

    def __init__(self, logger):
        self.logger = logger

    def run_pipeline(self, source_name, resources, out_dir):
        pipeline = PipelineFactory.create_pipeline(source_name, resources, out_dir, self.logger)
        result = pipeline.run()
        print(f"Pipeline finished with result: {result}")

