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

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from ..models.elections.election_results import ElectionResult
from ..serializers.election_serializer import ElectionResultSerializer
from django.db.models import Count  


from rest_framework import generics
from ..models import Election, ElectionResult
from ..serializers.election_serializer import ElectionSerializer, ElectionDetailSerializer, ElectionResultSerializer


class ElectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Election.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ElectionDetailSerializer
        return ElectionSerializer


class ElectionResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ElectionResult.objects.all()
    serializer_class = ElectionResultSerializer
