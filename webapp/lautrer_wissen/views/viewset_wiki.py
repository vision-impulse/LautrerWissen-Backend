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

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.http import Http404


from ..serializers.wiki_serializer import get_wiki_serializer_for_model


def create_wiki_viewset(model):
    """Dynamically create a ViewSet for list and detail views."""

    class GenericWikiViewSet(ReadOnlyModelViewSet):
        """API ViewSet for listing all objects and retrieving details."""

        def get_object(self):
            """Override default get_object to use virtual_id instead of pk."""
            pk = self.kwargs.get(self.lookup_field)
            for obj in model.objects.all():
                if obj.virtual_id == pk:
                    return obj
            raise Http404(f"{model.__name__} with virtual_id '{pk}' not found")

        def list(self, request):
            """Handles GET /api/{model_name}/"""
            objects = model.objects_for_list_view()

            objects = [
                {
                    "coordinate": (obj.geometry.y, obj.geometry.x),
                    "image_url": obj.image_url,
                    "image_license_url": obj.image_license_url,
                    "image_license_text": obj.image_license_text,
                    "image_author_name": obj.image_author_name,
                    "city_district_name": (
                        "Kaiserslautern Umkreis"
                        if obj.city_district_name == ""
                        else obj.city_district_name
                    ),
                    "name": obj.combined_name,
                    "id": obj.virtual_id,
                }
                for obj in objects
            ]

            return Response(
                {
                    "objects": objects,
                }
            )

        def retrieve(self, request, pk=None):
            """Handles GET /api/{model_name}/{id}/"""
            obj = self.get_object()

            serializer = get_wiki_serializer_for_model(obj, model)
            return Response(
                {
                    "object": serializer.data,
                }
            )

    return GenericWikiViewSet
