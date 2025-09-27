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

logger = logging.getLogger("ingestor")

def setup_django():
    """Initialize Django only if it's not already configured."""
    import django
    from django.conf import settings

    # already configured → skip setup
    if settings.configured:
        return

    # Default settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")

    try:
        django.setup()
        logger.info("Django successfully initialized.")
    except Exception as e:
        logger.error("Could not initialize Django: %s", e, exc_info=True)


def get_django_model(model_name, django_app="pipeline_manager"):
    try:
        import django
        from django.apps import apps
        if not django.apps.apps.ready:
            setup_django()
        return apps.get_model(django_app, model_name)
    except Exception as e:
        logger.error("Could not load Django model %s: %s", model_name, e, exc_info=True)
        return None