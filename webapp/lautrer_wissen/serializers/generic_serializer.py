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


def create_generic_serializer(model):
    """Dynamically creates and returns a serializer class for the given model."""
    class DynamicSerializer(serializers.ModelSerializer):
        def to_representation(self, instance):
            """Override to remove fields with NaN values."""
            data = super().to_representation(instance)

            return {key: value for key, value in data.items() if value != "NaN" }

        @classmethod
        def get_filtered_fields(cls):
            """Dynamically get fields, excluding those that might have NaN values."""
            return [field.name for field in model._meta.fields]  # Get all model fields

    # Dynamically create the Meta class and assign it to the serializer
    MetaClass = type("Meta", (), {"model": model, "fields": DynamicSerializer.get_filtered_fields()})
    setattr(DynamicSerializer, "Meta", MetaClass)

    return DynamicSerializer