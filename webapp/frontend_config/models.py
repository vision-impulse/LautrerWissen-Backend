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


class MapLayerGroup(models.Model):
    title = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#000000')  # Hex color code like '#f06292'
    order = models.PositiveIntegerField(default=0)  # Optional: for sorting

    class Meta:
        ordering = ['order']


class MapLayer(models.Model):
    group = models.ForeignKey(MapLayerGroup, related_name='layers', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='sublayers', on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    url = models.CharField(max_length=255)
    visible = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default='#000000')  # Allow per-layer override
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

