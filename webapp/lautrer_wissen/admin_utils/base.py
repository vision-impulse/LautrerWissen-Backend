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

from django.contrib import admin
from django.db import models


class CustomAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        if hasattr(self.model, 'MAP_FIELDS'):
            return list(self.model.MAP_FIELDS.keys())
        else:
            return [
                field.name for field in self.model._meta.get_fields()
                if isinstance(field, models.Field) and not field.many_to_many and not field.one_to_many
            ]