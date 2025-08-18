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

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from ..models import MODELS_WITH_DETAIL_PAGE


class BaseGeoSerializer(GeoFeatureModelSerializer):
    id = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    geometry = serializers.SerializerMethodField()

    def get_geometry(self, obj):
        """
        Compute geometry if the model does not have a `geometry` field.
        Otherwise, use the existing geometry field.
        """
        if hasattr(obj, "geometry") and obj.geometry:  # If model has geometry, use it
            if obj.geometry.geom_type == "LineString":
                return {
                    "type": "LineString",
                    "coordinates": [list(coord) for coord in obj.geometry.coords]
                }

            if obj.geometry.geom_type == "MultiPolygon":
                return {
                    "type": "MultiPolygon",
                    "coordinates": [list(coord) for coord in obj.geometry.coords[0]]
                }

            if obj.geometry.geom_type == "Polygon":
                return {
                    "type": "Polygon",
                    "coordinates": [list(coord) for coord in obj.geometry.coords[0]]
                }
            elif obj.geometry.geom_type == "Point":
                return {
                    "type": "Point",
                    "coordinates": [obj.geometry.x, obj.geometry.y]
                }
        elif hasattr(obj, "latitude") and hasattr(obj, "longitude"):  # Compute if missing
            return {
                "type": "Point",
                "coordinates": [float(obj.longitude), float(obj.latitude)]
            }
        return None  # Fallback if no geometry

    def get_properties(self, obj, request=None):
        """
        Custom logic to format response based on MAP_FIELDS,
        renaming fields accordingly and handling geometry transformations.
        """
        fields_mapping = getattr(obj.__class__, 'MAP_FIELDS', {})
        properties = {}

        visible_object_name = getattr(obj.__class__, 'VISIBLE_OBJECT_NAME', "")
        if visible_object_name != "":
            properties["Objektart"] = visible_object_name

        # Rename and select only fields listed in MAP_FIELDS
        for model_field, response_field in fields_mapping.items():
            val = getattr(obj, model_field, None)
            if val is not None and val != "":
                properties[response_field] = val

        if obj.__class__.__name__ in ["WikiBrewery", "WikiFishSculpture", "WikiCulturalMonument", 
                                      "WikiNaturalMonument", "WikiFountain", "WikiNaturalReserve", 
                                      "WikiSacralBuilding", "WikiRitterstein", "WikiStolperstein", 
                                      'KLSensorGrafanaDashboard']:
            properties[obj.get_frontend_url_name()] = obj.get_frontend_url()

        # Add ID
        properties["id"] = obj.id
        if self._should_use_virtual_id(obj):
            properties["id"] = obj.virtual_id

        return properties

    def get_id(self, obj, ):
        """
        Custom logic to return object depending on specific model 
        (use virtual_ids for specific models).
        """
        if self._should_use_virtual_id(obj):
            return obj.virtual_id
        return obj.id

    def _should_use_virtual_id(self, obj):
        return obj.__class__ in MODELS_WITH_DETAIL_PAGE and hasattr(obj, "virtual_id")


def create_geo_serializer(model):
    """Dynamically create a serializer for a given model."""

    serializer_name = f"{model.__name__}Serializer"
    serializer_attrs = {
        "Meta": type(
            "Meta",
            (),
            {
                "model": model,  # Dynamically set model
                "geo_field": "geometry", #if hasattr(model, "geometry") else None,
                "fields": ["id", "properties"],
            },
        ),
        "geometry": serializers.SerializerMethodField(),
        "get_geometry": BaseGeoSerializer.get_geometry,
    }
    return type(serializer_name, (BaseGeoSerializer,), serializer_attrs)