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


class BaseModel(models.Model):

    data_source = models.CharField(max_length=255, null=True)
    data_acquisition_date = models.DateField(null=True)
    city_district_name = models.CharField(max_length=255, default="", null=True)
    insert_timestamp = models.DateTimeField(null=True)

    class Meta:
        abstract = True  # This ensures Django does NOT create a separate table

    MAP_FIELDS = {
        "data_source": "Datenquelle",
        "city_district_name": "Stadtteil",
        "data_acquisition_date": "Aktualisiert am ",
    }