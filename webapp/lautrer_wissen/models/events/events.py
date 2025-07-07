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

from django.contrib.gis.db import models
from ..base_model import BaseModel


class KLCouncilEvent(BaseModel):
    committee = models.CharField(max_length=255)
    date = models.DateField()
    time = models.CharField(max_length=20) 
    location = models.TextField()
    category = models.CharField(max_length=100)
    title = models.TextField()
    link = models.URLField(blank=True)


class KLLeisureEvent(BaseModel):
    id = models.AutoField(primary_key=True)
    event_id = models.TextField()
    type = models.IntegerField()
    deleted = models.IntegerField()
    upcoming = models.IntegerField()

    caption_addition = models.TextField(null=True, blank=True)
    caption = models.TextField(null=True, blank=True)
    icon = models.TextField(null=True, blank=True)
    teaser = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    tickets = models.IntegerField(null=True, blank=True)
    category = models.TextField(null=True, blank=True)
    location_id = models.IntegerField(null=True, blank=True)

    location_name = models.TextField(null=True, blank=True)
    location_street = models.TextField(null=True, blank=True)
    location_pobox = models.IntegerField(null=True, blank=True)
    location_city = models.TextField(null=True, blank=True)

    dstart = models.DateTimeField()
    dend = models.DateTimeField()
    created = models.DateTimeField()
    updated = models.DateTimeField()


class WGAEvent(BaseModel):
    id = models.AutoField(primary_key=True)
    event_id = models.TextField(primary_key=False)  # Corresponds to 'id'
    title = models.TextField(max_length=255, null=True, blank=True)  # 'titel'
    date = models.DateField()  # 'datum'
    time = models.TextField()  # 'zeit'
    location = models.CharField(max_length=255)  # 'location'
    category = models.CharField(max_length=255, null=True, blank=True)  # 'kategorie'
    subtitle = models.TextField(max_length=255, null=True, blank=True)  # 'subtitel'
    description = models.TextField(null=True, blank=True)  # 'beschreibung'
    city = models.CharField(max_length=255)  # 'ort'
    postal_code = models.CharField(max_length=10, null=True, blank=True)  # 'plz'
    street = models.CharField(max_length=255, null=True, blank=True)  # 'strasse'
    location_url = models.URLField(null=True, blank=True)  # 'location_url'
    location_image = models.URLField(null=True, blank=True)  # 'location_bild'
    location_id = models.TextField(null=True, blank=True)  # 'location_id'
    sublocation = models.CharField(max_length=255, null=True, blank=True)  # 'sublocation'

    latitude = models.FloatField()  # 'lat'
    longitude = models.FloatField()  # 'lng'

    event_url = models.URLField(null=True, blank=True)  # 'url'
    youtube_video = models.CharField(max_length=255, null=True, blank=True)  # 'youtube'
    group_id = models.TextField(null=True, blank=True)  # 'groupid'
    date_iso = models.TextField(null=True, blank=True)  # 'datum_iso'
