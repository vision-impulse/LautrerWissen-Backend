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
from ..forms import GeoForm
from frontend_config.utils import get_model_field_mapping

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django import forms


class CustomAdmin(admin.ModelAdmin):

    def get_list_display(self, request):

        fields, _ = get_model_field_mapping(self.model)
        if len(fields) > 0:
            return list(fields.keys())
        else:
            return [
                field.name for field in self.model._meta.get_fields()
                if isinstance(field, models.Field) and not field.many_to_many and not field.one_to_many
            ]

class CustomGeoAdmin(CustomAdmin):

    form = GeoForm
    exclude = ("geometry",)


class CustomAdminMixin:
    class Media:
        css = {
            'all': ('admin/custom_admin.css',)
        }

admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(CustomAdminMixin, UserAdmin):
    pass

admin.site.unregister(Group)
@admin.register(Group)
class CustomGroupAdmin(CustomAdminMixin, GroupAdmin):
    pass

