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

import os
import logging

from django.core.management.base import BaseCommand
from pipeline_manager.models import Pipeline
from pipeline_manager.models import ResourceOSM
from pipeline_manager.models import ResourceWFSFile
from pipeline_manager.models import LocalResourceFile
from pipeline_manager.models import ResourceWikipage
from pipeline_manager.models import RemoteResourceFile
from pipeline_manager.models import WGAResourceFile
from pipeline_manager.models import EmergencyPointResourceFile
from pipeline_manager.models import EVResourceFile
from pipeline_manager.models import VRNResourceFile

from ingestor.datapipe.pipeline_config import load_config
from settings_seedfiles import SEED_FILES

logger = logging.getLogger("webapp")


class Command(BaseCommand):
    help = "Import data resources from YAML config"

    def add_arguments(self, parser):
        parser.add_argument(
            "--pipeline_config",
            type=str,
            required=False,
            help="Path to the pipeline config file.",
        )
        parser.add_argument(
            "--override_existing",
            action="store_true",
            required=False,
            help="If set, will override existing pipeline data.",
        )

    def handle(self, *args, **kwargs):
        config_path = kwargs["pipeline_config"]
        override_existing = kwargs.get("override_existing", False)

        if config_path is None or not os.path.exists(config_path):
            logger.info("Using default config path")
            config_path = SEED_FILES["data_sources_config"]

        if not os.path.exists(config_path):
            return

        config = load_config(config_path)
        logger.info("Loaded config %s", config_path)

        for pipeline_type, pipeline_config in config.pipelines.items():
            description = pipeline_config.description
            resources = pipeline_config.resources
            if override_existing:
                try:
                    existing_pipeline = Pipeline.objects.get(name=pipeline_type.name)
                    existing_pipeline.delete()  # This cascades to related resource objects
                    logger.info("Deleted existing pipeline: %s", pipeline_type.name)
                except Pipeline.DoesNotExist:
                    pass  # Nothing to delete

            pipeline, created = Pipeline.objects.get_or_create(
                name=pipeline_type.name, defaults={"description": description}
            )
            if not created and pipeline.description != description:
                pipeline.description = description
                pipeline.save(update_fields=["description"])
            if created:
                for res in resources:
                    model_cls = {
                        "ResourceOSM": ResourceOSM,
                        "ResourceWFSFile": ResourceWFSFile,
                        "LocalResourceFile": LocalResourceFile,
                        "RemoteResourceFile": RemoteResourceFile,
                        "ResourceWikipage": ResourceWikipage,
                        "WGAResourceFile": WGAResourceFile,
                        "VRNResourceFile": VRNResourceFile,
                        "EVResourceFile": EVResourceFile,
                        "EmergencyPointResourceFile": EmergencyPointResourceFile,
                    }.get(res.__class__.__name__, None)

                    if not model_cls:
                        logger.warning("Unknown resource type: %s", res)
                        continue

                    model_cls.objects.create(pipeline=pipeline, **res.__dict__)
                    logger.info("Created resource: %s", model_cls)
                logger.info("Created pipeline: %s", pipeline.name)
