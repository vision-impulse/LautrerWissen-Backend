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

from django.db import models


class DockerContainerStatus(models.Model):

    class Meta:
        managed = True
        verbose_name = "Docker Containers"
        verbose_name_plural = "Docker Containers"

    name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, blank=True)
    log_file = models.CharField(max_length=500, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True)


class MonitoringDashboard(models.Model):
    class Meta:
        managed = False  # no table
        verbose_name = "NGINX Dashboard"
        verbose_name_plural = "NGINX Analysis"

