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


class ModelConfig(models.Model):
    app_label = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_display_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ("app_label", "model_name")
        verbose_name = "Model Configuration"
        verbose_name_plural = "Model Configurations"


class ModelFieldConfig(models.Model):
    model_config = models.ForeignKey(
        ModelConfig, on_delete=models.CASCADE, related_name="fields"
    )
    field_name = models.CharField(max_length=100)
    visible = models.BooleanField(default=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ("model_config", "field_name")
        verbose_name = "Field Configuration"
        verbose_name_plural = "Field Configurations"


ModelConfig._meta.app_label = "frontend_config"
ModelFieldConfig._meta.app_label = "frontend_config"
