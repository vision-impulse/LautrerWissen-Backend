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

from frontend_config.model_field_config import ModelConfig, ModelFieldConfig
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

import logging

logger = logging.getLogger("webapp")


def get_model_field_mapping(model_class):
    """
    Return dynamic MAP_FIELDS and visible object name from DB or fall back to class attributes.

    Handles:
    - No DB config found
    - Multiple configs found
    - Missing or invalid field configs
    - Falls back to class defaults cleanly
    """

    app_label = "lautrer_wissen"
    model_name = model_class._meta.model_name

    visible_object_name = getattr(model_class, "VISIBLE_OBJECT_NAME", "")
    base_map_fields = getattr(model_class, "MAP_FIELDS", {})
    mapping = base_map_fields.copy()

    try:
        configs = (
            ModelConfig.objects.filter(app_label=app_label, model_name=model_name)
            .prefetch_related("fields")
        )

        if not configs.exists():
            logger.debug(f"No ModelConfig found for {app_label}.{model_name}; using defaults.")
            return mapping, visible_object_name

        config = configs.first()

        # Apply visible name override if provided
        if config.object_display_name:
            visible_object_name = config.object_display_name

        # Apply per-field overrides
        for field_conf in config.fields.all():
            # Skip broken configs
            if not hasattr(field_conf, "field_name"):
                logger.warning(f"Ignoring invalid field config on {config}: {field_conf}")
                continue

            if not field_conf.visible:
                mapping.pop(field_conf.field_name, None)
            else:
                mapping[field_conf.field_name] = (
                    field_conf.display_name
                    or mapping.get(field_conf.field_name, field_conf.field_name)
                )
    except Exception as e:
        logger.exception(f"Error loading ModelConfig for {app_label}.{model_name}: {e}")

    return mapping, visible_object_name
