#!/usr/bin/env python
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
from frontend_config.model_field_config import ModelConfig, ModelFieldConfig
from settings_seedfiles import SEED_FILES


logger = logging.getLogger("webapp")


class Command(BaseCommand):
    help = "Import model and field configurations from YAML"

    def handle(self, *args, **options):
        model_field_config_fp = SEED_FILES["models_field_config"]
        with open(model_field_config_fp, "r") as f:
            data = yaml.safe_load(f)

        for m in data.get("models", []):
            model_cfg, _ = ModelConfig.objects.update_or_create(
                app_label=m["app_label"],
                model_name=m["model_name"].lower(),
                defaults={"object_display_name": m.get("display_name")},
            )

            for f_cfg in m.get("fields", []):
                ModelFieldConfig.objects.update_or_create(
                    model_config=model_cfg,
                    field_name=f_cfg["field_name"],
                    defaults={
                        "visible": f_cfg.get("visible", False),
                        "display_name": f_cfg.get("display_name"),
                    },
                )
        logger.info("Imported model configurations successfully")
