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
import yaml

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from lautrer_wissen.models.geo.kl import KLSensorGrafanaDashboard
from settings_seedfiles import SEED_FILES

logger = logging.getLogger("webapp")


class Command(BaseCommand):
    help = "Import grafana dashboard objects into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reimport even if existing data is present",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if not force and KLSensorGrafanaDashboard.objects.exists():
            logger.warning(
                "Grafana dashboards already exist. Import will be skipped. " \
                "Use python3 manage.py import_dashboards --force to overwrite."
            )
            return

        if force:
            logger.info("Deleting existing dashboards data.")
            KLSensorGrafanaDashboard.objects.all().delete()
        self._import_dashboards()

    def _import_dashboards(self):
        with open(SEED_FILES["dashboard_data_file"], "r") as f:
            data = yaml.safe_load(f)
            for entry in data:
                obj, created = KLSensorGrafanaDashboard.objects.get_or_create(
                    name=entry["name"],
                    timefilters=entry["timefilters"],
                    defaults={
                        "dashboard_url": entry["dashboard_url"],
                        "geometry": Point(entry["lon"], entry["lat"]),
                        "size_radius_meters": entry.get("size_radius_meters", 10),
                        "timefilters": entry.get("timefilters", "täglich"),
                    }
                )
                if created:
                    logger.info(f"Created new dashboard object (%s)!", obj.name)
                else:
                    logger.info(f"Skipped existing dashboard (%s)!", obj.name)
            logger.info(f"All Grafana dashboards successfully imported.")
