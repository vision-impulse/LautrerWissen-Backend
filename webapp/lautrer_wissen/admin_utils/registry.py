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
from django.apps import apps
from .base import CustomAdmin
from .base import CustomGeoAdmin
from .qr_admin import CustomAdminWithQR
from lautrer_wissen.models import MODELS_WITH_DETAIL_PAGE, API_GEO_MODELS


app_models = apps.get_app_config('lautrer_wissen').get_models()


for model in app_models:
    if model in MODELS_WITH_DETAIL_PAGE:
        admin_class = type(f'{model.__name__}AdminWithQR', (CustomAdminWithQR,), {'model': model})
    elif model in API_GEO_MODELS:
        admin_class = type(f'{model.__name__}CustomGeoAdmin', (CustomGeoAdmin,), {'model': model})
    else:
        admin_class = type(f'{model.__name__}Admin', (CustomAdmin,), {'model': model})

    model_name = getattr(model, 'ADMIN_DISPLAY_NAME', model.__name__)
    model._meta.verbose_name = model_name
    model._meta.verbose_name_plural = model_name

    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass