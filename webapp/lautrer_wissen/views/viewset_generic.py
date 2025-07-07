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

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination

from ..serializers.generic_serializer import create_generic_serializer


def create_generic_viewset(model):
    """Dynamically create a viewset for a given model."""

    serializer_class = create_generic_serializer(model)  # Generate serializer dynamically

    viewset_name = f"{model.__name__}ViewSet"

    return type(
        viewset_name,
        (viewsets.ReadOnlyModelViewSet,),  # Inherit from ModelViewSet
        {
            "queryset": model.objects.all(),  # Assign queryset dynamically
            "serializer_class": serializer_class,  # Assign serializer dynamically
            "filter_backends": [DjangoFilterBackend, OrderingFilter, SearchFilter],
            "search_fields": ["name"] if "name" in [f.name for f in model._meta.get_fields()] else [],
            "ordering_fields": ["id"],
            "pagination_class": PageNumberPagination,
        },
    )