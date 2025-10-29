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

from django.apps import AppConfig


class LautrerWissenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lautrer_wissen'
    verbose_name = "Daten-Modelle"

    def ready(self):
        from django.apps import apps
        from django.conf import settings

        icons = getattr(settings, "JAZZMIN_SETTINGS", {}).get("icons", {})
        icons["lautrer_wissen"] = "fas fa-database"
        for model in apps.get_app_config("lautrer_wissen").get_models():
            icons[f"lautrer_wissen.{model.__name__}"] = "fas fa-table"
        settings.JAZZMIN_SETTINGS["icons"] = icons
