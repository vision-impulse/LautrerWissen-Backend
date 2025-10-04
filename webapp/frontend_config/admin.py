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

from django.contrib import admin, messages
from django import forms
from django.utils.safestring import mark_safe
from django.apps import apps
from django.shortcuts import render, redirect
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.template.response import TemplateResponse
from .model_field_config import ModelConfig, ModelFieldConfig
from .models import MapLayerGroup, MapLayer


class LayerInline(admin.TabularInline):
    model = MapLayer
    extra = 1


@admin.register(MapLayerGroup)
class LayerGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "color", "order")
    inlines = [LayerInline]


EXCLUDED_FIELDS = {"id", "pk", "created_at", "updated_at", "virtual_id", 'geometry'}


class ModelFieldConfigInline(admin.TabularInline):
    model = ModelFieldConfig
    extra = 0
    fields = ("field_name", "visible", "display_name")
    can_delete = True
    show_change_link = False
    ordering = ("field_name",)

    def get_formset(self, request, obj=None, **kwargs):
        """
        Dynamically ensure ModelFieldConfig objects exist for all fields
        of the related model when editing a ModelConfig.
        """
        if obj:  
            try:
                model_class = apps.get_model(obj.app_label, obj.model_name)
            except LookupError:
                messages.warning(
                    request, f"Model '{obj.app_label}.{obj.model_name}' not found."
                )
                return super().get_formset(request, obj, **kwargs)

            # All actual model field names
            all_fields = [
                f.name
                for f in model_class._meta.fields
                if f.name not in EXCLUDED_FIELDS
            ]

            # Existing field configs
            existing_configs = {f.field_name: f for f in obj.fields.all()}

            # Create missing ModelFieldConfig objects (not yet in DB)
            for field_name in all_fields:
                if field_name not in existing_configs:
                    ModelFieldConfig.objects.create(
                        model_config=obj,
                        field_name=field_name,
                        visible=False,  # default hidden
                        display_name=field_name.replace("_", " ").capitalize(),
                    )

            # Optionally remove configs for fields no longer in the model
            obsolete = [f for f in obj.fields.all() if f.field_name not in all_fields]
            if obsolete:
                for o in obsolete:
                    o.delete()
                messages.warning(
                    request,
                    f"Removed obsolete field configs: {', '.join(o.field_name for o in obsolete)}",
                )

        return super().get_formset(request, obj, **kwargs)


@admin.register(ModelConfig)
class ModelConfigAdmin(admin.ModelAdmin):
    inlines = [ModelFieldConfigInline]
    list_display = ("app_label", "model_name", "object_display_name")
    search_fields = ("app_label", "model_name")
    readonly_fields = ("app_label", "model_name")

    # override app label for sidebar grouping
    def get_model_perms(self, request):
        """Show under frontend_config app in the admin."""
        perms = super().get_model_perms(request)
        perms["view"] = True
        return perms

    def changelist_view(self, request, extra_context=None):
        # Build list of all models from installed apps
        all_models = [
            (m._meta.app_label, m._meta.model_name)
            for m in apps.get_models()
            if not m._meta.proxy
        ]
        all_models = [
            (app_label, model_name)
            for (app_label, model_name) in all_models
            if app_label == "lautrer_wissen"
        ]

        existing = set(ModelConfig.objects.values_list("app_label", "model_name"))
        missing = [(a, m) for a, m in all_models if (a, m) not in existing]
        extra = [
            cfg
            for cfg in ModelConfig.objects.all()
            if (cfg.app_label, cfg.model_name) not in all_models
        ]

        if extra:
            messages.warning(
                request,
                f"The following ModelConfigs no longer match models: {', '.join(str(e) for e in extra)}",
            )

        # Sync ModelConfig entries only for existing models, if not already present
        for app_label, model_name in missing:
            ModelConfig.objects.create(app_label=app_label, model_name=model_name)

        return super().changelist_view(request, extra_context)


admin.site._registry[MapLayerGroup].model._meta.verbose_name = "Sidebar Karte"
admin.site._registry[MapLayerGroup].model._meta.verbose_name_plural = "Sidebar Karte"

admin.site._registry[ModelConfig].model._meta.verbose_name = (
    "Daten-Modelle"
)
admin.site._registry[ModelConfig].model._meta.verbose_name_plural = (
    "Daten-Modelle"
)
