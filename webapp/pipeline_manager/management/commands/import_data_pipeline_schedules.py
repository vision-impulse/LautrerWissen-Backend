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

import yaml
import logging

from django.core.management.base import BaseCommand
from settings_seedfiles import SEED_FILES
from pipeline_manager.models import PipelineSchedule

logger = logging.getLogger("webapp")


class Command(BaseCommand):
    help = "Import pipeline cronjobs from YAML if they do not already exist."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reimport even if existing data is present",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if not force and PipelineSchedule.objects.exists():
            logger.warning(
                "PipelineSchedule already exist. Import will be skipped. " \
                "Use python3 manage.py import_data_pipeline_schedules --force to overwrite."
            )
            return

        if force:
            logger.info("Deleting existing pipeline cronjobs.")
            PipelineSchedule.objects.all().delete()
        self._import_pipeline_schedules()

    def _import_pipeline_schedules(self):
        config_path = SEED_FILES["data_sources_schedules_config"]
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        for p in config.get('pipelines', []):
            obj, created = PipelineSchedule.objects.get_or_create(
                name=p['name'],
                defaults={'cron_expression': p['cron_expression'], 'is_active': True}
            )
            if created:
                logger.info("Added schedule for: %s." %(p['name']))
            else:
                logger.info("Schedule for %s already exists." %(p['name']))
