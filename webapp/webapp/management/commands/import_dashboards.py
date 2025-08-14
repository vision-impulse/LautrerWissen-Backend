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
 
import json
import yaml
import os 
import pandas as pd
import logging

from django.core.management.base import BaseCommand
from lautrer_wissen.models.geo.kl import KLSensorGrafanaDashboard
from django.contrib.gis.geos import Point

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Import grafana-dashboard objects into the database"

    def handle(self, *args, **kwargs):
        yaml_file = os.path.join(os.getenv("APP_DATA_DIR"), "initial/data/dashboards.yaml")
        with open(yaml_file, "r") as f:
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

        logger.info(f"All GrafanaDashboards successfully imported!")
