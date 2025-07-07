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
 
import sys
import logging

from django.core.management.base import BaseCommand
from pipeline_manager.models import Pipeline

from ingestor.datapipe.manager import PipelineManager
from ingestor.datapipe.pipelines.base_pipeline import PipelineType
import os
from datetime import date

class ClassNameFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, 'classname'):
            record.classname = f"[{record.classname}]"
        else:
            record.classname = "[UnknownClass]"
        return super().format(record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('downloader.log')
formatter = ClassNameFormatter('%(asctime)s - %(levelname)s - %(classname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
   
   
class Command(BaseCommand):
    help = "Execute a specific pipeline"

    def add_arguments(self, parser):
        parser.add_argument('pipeline_name', type=str)

    def _get_import_folder(self):
        data_folder = os.getenv("APP_DATA_DIR", "./data/") # Fallback    
        data_import_folder = os.path.join(data_folder, "data_import", date.today().strftime("%Y_%m_%d"))
        os.makedirs(data_import_folder, exist_ok=True)
        return data_import_folder

    def _get_resources_for_pipeline(self, pipeline):
        resources = []
        if hasattr(pipeline, 'osm_resources'):
            resources.extend(pipeline.osm_resources.all())
        if hasattr(pipeline, 'wfs_resources'):
            resources.extend(pipeline.wfs_resources.all())
        if hasattr(pipeline, 'local_resources'):
            resources.extend(pipeline.local_resources.all())
        if hasattr(pipeline, 'wikipage_resources'):
            resources.extend(pipeline.wikipage_resources.all())
        if hasattr(pipeline, 'remote_resources'):
            resources.extend(pipeline.remote_resources.all())
        
        # Now you can loop over them or do processing
        self.stdout.write(f"Found {len(resources)} total resources:")
        for res in resources:
            self.stdout.write(f"- {res}")
        return resources

    def handle(self, *args, **kwargs):
        name = kwargs['pipeline_name']
        pipeline = Pipeline.objects.get(name=name)
        resources = self._get_resources_for_pipeline(pipeline)

        data_import_folder = self._get_import_folder() 

        manager = PipelineManager(logger)        
        self.stdout.write(f"Running pipeline: {name}")
        manager.run_pipeline(name, resources, data_import_folder)
    