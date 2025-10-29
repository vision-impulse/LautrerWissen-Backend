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

import re
import json
import os
import logging

from django.core.management.base import BaseCommand
from monitoring.models import DockerContainerStatus
from django.utils import timezone

logger = logging.getLogger("webapp")


class Command(BaseCommand):
    help = "Sync docker container statuses from JSON file into the database."

    def handle(self, *args, **options):
        file_path = "/logs/analysis/docker_status.json"

        if not os.path.exists(file_path):
            logger.error("File not found: %s", file_path)
            return

        try:
            with open(file_path, "r") as f:
                content = f.read()  # .strip()
                data = json.loads(content)
        except Exception as e:
            logger.error("Failed to parse JSON: %s", e)
            return

        updated, created = 0, 0
        for entry in data["status_checks"]:
            name = entry.get("service_name")
            status = entry.get("status")
            log_file = entry.get("log_file")

            if not name:
                continue

            try:
                obj = DockerContainerStatus.objects.filter(name=name).first()
                if obj:
                    # update only if status changed
                    if obj.status != status:
                        obj.status = status
                        obj.log_file = log_file
                        obj.last_updated = timezone.now()
                        obj.save(update_fields=["status", "log_file", "last_updated"])
                        updated += 1
                else:
                    DockerContainerStatus.objects.create(
                        name=name, status=status, log_file=log_file
                    )
                    created += 1
            except Exception as e:
                logger.error("Error updating %s: %s", name, e)
        logger.info("Sync complete. Updated: %s, Created: %s", updated, created)
