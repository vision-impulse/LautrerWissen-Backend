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

from django.core.management.base import BaseCommand
from frontend_config.models import MapLayerGroup, MapLayer
from settings_seedfiles import SEED_FILES

import json
import os
import logging

logger = logging.getLogger("webapp")


class Command(BaseCommand):
    help = "Import sidebar config for the frontend into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reimport even if existing data is present",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if not force and MapLayerGroup.objects.exists():
            logger.warning(
                "Sidebar config data already exists. Import will be skipped. " \
                "Use python3 manage.py import_maplayer_config --force to overwrite."
            )
            return

        if force:
            logger.info("Deleting existing sidebar configuration.")
            MapLayerGroup.objects.all().delete()
            MapLayer.objects.all().delete()

        self._import_seed_data()

    def _import_seed_data(self):
        with open(SEED_FILES["sidebar_config"], "r", encoding="utf-8") as f:
            config = json.load(f)

            for group_order, group_data in enumerate(config):
                group, _ = MapLayerGroup.objects.get_or_create(
                    title=group_data["title"],
                    defaults={
                        "color": group_data.get("color", "#CCCCCC"),
                        "order": group_order,
                    },
                )

                for layer_order, layer_info in enumerate(group_data["layers"]):
                    layer = MapLayer.objects.create(
                        group=group,
                        name=layer_info["title"],
                        url=layer_info["url"],
                        visible=layer_info.get("visible", False),
                        color=layer_info.get("color", "#000000"),
                        order=layer_order,
                        parent=None,
                    )

                    sublayers = layer_info.get("subLayers", {})
                    for sub_order, layersub_info in enumerate(sublayers):
                        MapLayer.objects.create(
                            group=group,
                            parent=layer,
                            name=layersub_info["title"],
                            url=layersub_info["url"],
                            visible=layersub_info.get("visible", False),
                            color=layersub_info.get("color", "#000000"),
                            order=sub_order,
                        )
        logger.info("Sidebar config successfully imported.")
