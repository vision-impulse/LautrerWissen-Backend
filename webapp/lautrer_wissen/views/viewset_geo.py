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

from ..serializers.geo_serializers import create_geo_serializer

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, BooleanFilter
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Q
from django.db import models
import django_filters
from rest_framework.response import Response
import json
from frontend_config.utils import get_model_field_mapping

class MultiCategoryFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


def create_dynamic_geo_filter(model):
    """
    Return a FilterSet class for `model` that builds filters lazily on instantiation.
    This avoids DB access at import time and avoids async/sync ORM issues.
    """

    class DynamicGeoFilter(FilterSet):
        # Provide a Meta placeholder; we'll set .model after class creation.
        class Meta:
            model = None
            fields = []

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Compute mapping lazily (per-request time).
            try:
                fields_map, _visible_name = get_model_field_mapping(model)
            except Exception:
                fields_map = getattr(model, "MAP_FIELDS", {}) or {}

            rel_fields = []

            def is_missing_filter(queryset, name, value, *, field_name):
                if value: # ?field__missing=true
                    return queryset.filter(
                        models.Q(**{f"{field_name}__isnull": True}) | models.Q(**{f"{field_name}": ""})
                    )
                else: # ?field__missing=false
                    return queryset.exclude(
                        models.Q(**{f"{field_name}__isnull": True}) | models.Q(**{f"{field_name}": ""})
                    )
                
            # Attach dynamic filters to this instance
            for model_field_name, public_field_name in fields_map.items():
                try:
                    model_field = model._meta.get_field(model_field_name)
                except Exception:
                    # field not present in the model, skip it
                    continue

                if isinstance(model_field, (models.DateField, models.DateTimeField)):
                    continue
        
                rel_fields.append(public_field_name)

                self.filters[public_field_name] = CharFilter(field_name=model_field_name, lookup_expr="iexact")

                # Define a custom "not equal" filter function (e.g., `?access__ne=Kunden`)
                def ne_filter(queryset, name, value, field_name=model_field_name):
                    # Make sure to exclude where model_field_name matches value
                    return queryset.exclude(**{field_name: value})
                
                self.filters[f"{public_field_name}__ne"] = CharFilter(method=ne_filter)
                self.filters[f"{public_field_name}__in"] = MultiCategoryFilter(field_name=model_field_name,
                                                                                lookup_expr='in')
                
                self.filters[f"{public_field_name}__gte"] = django_filters.NumberFilter(
                        field_name=model_field_name, lookup_expr="gte")
            
                self.filters[f"{public_field_name}__missing"] = BooleanFilter(
                    method=lambda qs, name, value, field_name=model_field_name: 
                    is_missing_filter(qs, name, value, field_name=field_name)
                )

            # Update Meta.fields so introspection / docs see them
            try:
                self._meta.fields = rel_fields
            except Exception:
                pass

    # Safely set Meta.model and Meta.fields after class creation
    DynamicGeoFilter.Meta.model = model
    DynamicGeoFilter.Meta.fields = []  # we populate runtime filters in __init__
    return DynamicGeoFilter


def create_geo_viewset(model):
    """Dynamically create a viewset for a given model."""

    serializer_class = create_geo_serializer(model)
    dynamic_filter_class = create_dynamic_geo_filter(model)

    viewset_name = f"{model.__name__}ViewSet"

    if 'latitude' in [f.name for f in model._meta.get_fields()]:
        queryset = model.objects.filter(latitude__isnull=False)
    else:
        queryset = model.objects.all()

    def merge_features_by_geometry(feature_collection):
        merged = {}
        for feature in feature_collection["features"]:
            geometry = feature["geometry"]
            if isinstance(geometry, str):
                geometry = json.loads(geometry)

            geometry_key = tuple(geometry["coordinates"])
            if geometry_key not in merged:
                merged[geometry_key] = {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {}
                }

            for key, value in feature["properties"].items():
                if key not in merged[geometry_key]["properties"]:
                    merged[geometry_key]["properties"][key] = [value]
                else:
                    if value not in merged[geometry_key]["properties"][key]:
                        merged[geometry_key]["properties"][key].append(value)

        merged_features = []
        for feature in merged.values():
            props = feature["properties"]
            final_props = {}

            for key, values in props.items():
                final_props[key] = values[0] if len(values) == 1 else values

            if "size_radius_meters" in final_props:
                del final_props["size_radius_meters"]
            if "dashboard_url" in final_props:
                del final_props["dashboard_url"]
            if "timefilters" in final_props:
                del final_props["timefilters"]
            if "id" in final_props:
                del final_props["id"]
            feature["properties"] = final_props
            merged_features.append(feature)
        
        feature_collection["features"] = merged_features
        return feature_collection

    # Create a custom `list` method
    def merged_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        data = serializer.data

        # Merge overlapping features
        if model.__name__ in ["KLSensorGrafanaDashboard", 'WikiStolperstein']:
            data = merge_features_by_geometry(data)
        return Response(data)

    # Build the ViewSet class dynamically with type()
    return type(
        viewset_name,
        (viewsets.ReadOnlyModelViewSet,),
        {
            "queryset": queryset,
            "serializer_class": serializer_class,
            "ordering_fields": ["id"],
            "pagination_class": None,
            "filter_backends": [DjangoFilterBackend, OrderingFilter, SearchFilter],
            "filterset_class": dynamic_filter_class,
            "list": merged_list,  # Overriding list method
        },
    )