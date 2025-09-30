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
import os

from django.core.management.base import BaseCommand
from pipeline_manager.models import Pipeline, PipelineRun
from ingestor.datapipe.manager import PipelineManager
from ingestor.datapipe.pipelines.base_pipeline import PipelineType
from datetime import date
from django.utils import timezone

logger = logging.getLogger("webapp")

   
class Command(BaseCommand):
    help = "Execute a specific pipeline"

    def add_arguments(self, parser):
        parser.add_argument('pipeline_name', type=str)
        parser.add_argument(
            "--caller",
            type=str,
            default="manual",
            help="Indicates who triggered the pipeline"
        )

    def _get_import_folder(self):
        data_folder = os.getenv("APP_DATA_DIR", "./data/") # Fallback    
        data_import_folder = os.path.join(data_folder, "data_import", date.today().strftime("%Y_%m_%d"))
        os.makedirs(data_import_folder, exist_ok=True)
        return data_import_folder

    def _get_resources_for_pipeline(self, pipeline):
        resources = []
        if hasattr(pipeline, 'osm_resources'):
            resources.extend(pipeline.osm_resources.filter(active=True))
        if hasattr(pipeline, 'wfs_resources'):
            resources.extend(pipeline.wfs_resources.filter(active=True))
        if hasattr(pipeline, 'local_resources'):
            resources.extend(pipeline.local_resources.filter(active=True))
        if hasattr(pipeline, 'wikipage_resources'):
            resources.extend(pipeline.wikipage_resources.filter(active=True))
        if hasattr(pipeline, 'remote_resources'):
            resources.extend(pipeline.remote_resources.filter(active=True))
        return resources
    
    def handle(self, *args, **kwargs):
        name = kwargs['pipeline_name']
        caller = kwargs.get("caller", "manual")

        pipeline = Pipeline.objects.get(name=name)
        resources = self._get_resources_for_pipeline(pipeline)
        data_import_folder = self._get_import_folder() 
        logger.info("Running pipeline: %s", name)
        logger.info("Found %s total data sources:", len(resources))
        for res in resources:
            logger.info("Data source: %s, DB model: %s", res.data_source, res.db_model_class)

        try:
            pipeline_run = PipelineRun.objects.create(
                pipeline_name=name,
                origin=caller,
                status='running',
                started_at=timezone.now(),
            )
            manager = PipelineManager()        
            result = manager.run_pipeline(name, resources, data_import_folder, pipeline_run)
            status = 'success' if result == 'success' else 'failed'
            pipeline_run.status = status
            pipeline_run.finished_at = timezone.now()
            pipeline_run.save()
        except Exception as exc:
            pipeline_run.status = 'failed'
            pipeline_run.error_message = str(exc)
            pipeline_run.finished_at = timezone.now()
            pipeline_run.save()
