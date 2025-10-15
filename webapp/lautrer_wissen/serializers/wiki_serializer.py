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

from abc import abstractmethod

from rest_framework import serializers
from frontend_config.utils import get_model_field_mapping


def get_wiki_serializer_for_model(obj, model):
    """Dynamically create a serializer class for the given model."""

    DynamicSerializer = type(
        f"{model.__name__}Serializer",  # Dynamically set class name
        (WikiBaseObjectSerializer,),  # Inherit from base serializer
        {
            "Meta": type(
                "Meta",
                (WikiBaseObjectSerializer.Meta,),  # Inherit base Meta
                {"model": model},  # Assign the correct model dynamically
            )
        },
    )
    return DynamicSerializer(obj)


class WikiBaseObjectSerializer(
    serializers.ModelSerializer, metaclass=type(serializers.ModelSerializer)
):
    id = serializers.SerializerMethodField()
    nearby_objects = serializers.SerializerMethodField()
    coordinate = serializers.SerializerMethodField()
    fields_to_display = serializers.SerializerMethodField()
    image_info = serializers.SerializerMethodField()
    references = serializers.SerializerMethodField()
    object_type = serializers.SerializerMethodField()
    wikipedia_link = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "wikipedia_link",
            "object_type",
            "fields_to_display",
            "image_info",
            "coordinate",
            "nearby_objects",
            "references",
        ]
        abstract = True  # Ensure the base serializer is not instantiated

    def get_id(self, obj):
        return obj.virtual_id

    def get_wikipedia_link(self, obj):
        return obj.__class__.WIKI_OBJECT_URL

    def get_object_type(self, obj):
        return obj.__class__.VISIBLE_OBJECT_NAME

    def get_image_info(self, obj):
        return obj.get_image_info()

    def get_fields_to_display(self, obj):
        mapping, _ = get_model_field_mapping(obj.__class__)
        display_data = {}
        for model_field, display_name in mapping.items():
            value = getattr(obj, model_field, None)
            display_data[display_name] = value
        return display_data

    def get_references(self, obj):
        return list(obj.get_references())

    def get_coordinate(self, obj):
        """Returns the latitude and longitude of the object."""
        return {
            "latitude": obj.geometry.x,
            "longitude": obj.geometry.y,
        }

    def get_nearby_objects(self, obj):
        """Returns nearby objects based on the model type."""
        return obj.__class__.nearby_objects_as_dict(obj)
