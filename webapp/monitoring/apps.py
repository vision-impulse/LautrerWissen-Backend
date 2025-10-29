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

from django.apps import AppConfig
from django.conf import settings
import sys

class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'
    verbose_name = "System-Monitoring"

    def ready(self):
        if (
            "makemigrations" in sys.argv
            or "migrate" in sys.argv
            or "collectstatic" in sys.argv
            or "shell" in sys.argv
        ):
            return

        if settings.SCHEDULER_ENABLED:
            from django.dispatch import receiver

            from . import scheduler
            scheduler.start()
