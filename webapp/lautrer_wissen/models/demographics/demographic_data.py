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

class DemographicData(models.Model):
    city_district_id = models.CharField(max_length=100, null=True, default=None)
    city_district_name = models.CharField(max_length=255, null=True, default=None)
    age_group = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    population_count = models.IntegerField(default=0)
    reporting_date = models.DateField()
    remark = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    data_source = models.CharField(max_length=255, null=True)
    data_acquisition_date = models.DateField(null=True)
    insert_timestamp = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "Demographic Data"
        verbose_name_plural = "Demographic Data"
                    