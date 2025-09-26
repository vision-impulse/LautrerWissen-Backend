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
from django.utils.timezone import now  

from ..serializers.generic_serializer import create_generic_serializer

import django_filters
from ..models.events.events import KLLeisureEvent
from ..models.events.events import WGAEvent
from ..models.events.events import KLCouncilEvent
from ..models import KLConstructionSite
from ..models import DemographicData
from ..models import KLSensorGrafanaDashboard

from datetime import datetime
from rest_framework.response import Response
from rest_framework.decorators import action

# ------------------------------------------------------------------------------------

class MultiCategoryFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class KLLeisureEventFilter(django_filters.FilterSet):
    category = MultiCategoryFilter(field_name='category', lookup_expr='in')
    upcoming = django_filters.CharFilter(lookup_expr="iexact")
    start_date = django_filters.DateFilter(field_name="dstart", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="dend", lookup_expr="lte")

    class Meta:
        model = KLLeisureEvent
        fields = ["category", "upcoming", "start_date", "end_date"]


class KLWGAEventFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(lookup_expr="iexact")
    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = WGAEvent
        fields = ["category", "start_date", "end_date"]


class KLCouncilEventFilter(django_filters.FilterSet):
    category = MultiCategoryFilter(field_name='category', lookup_expr='in')
    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = KLCouncilEvent
        fields = ["category", "date"]


class ConstructionSiteFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(lookup_expr="iexact")
    start_date = django_filters.DateFilter(field_name="baustart", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="bauende", lookup_expr="lte")

    class Meta:
        model = KLConstructionSite
        fields = ["bez", "baustart", "bauende"]


class DemographicDataFilter(django_filters.FilterSet):
    city_district_id = django_filters.CharFilter(lookup_expr="iexact")
    
    class Meta:
        model = DemographicData
        fields = ["city_district_id", ]


# ------------------------------------------------------------------------------------


class KLLeisureEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = create_generic_serializer(KLLeisureEvent)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = KLLeisureEventFilter
    search_fields = ['caption', 'caption_addition', 'description'] # category?
    ordering_fields = ['id', 'dstart',]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        today = datetime.now().date()
        return KLLeisureEvent.objects.filter(
            dstart__gte=today
        ).exclude(
            deleted=1
        ).order_by('dstart')


class KLWGAEventViewSet(viewsets.ReadOnlyModelViewSet):
    
    serializer_class = create_generic_serializer(WGAEvent)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = KLWGAEventFilter
    search_fields = ['title', 'subtitle', 'description']
    ordering_fields = ['id', 'date',]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        today = datetime.now().date()
        return WGAEvent.objects.filter(
            date__gte=today
        ).order_by('date')
    

class KLCouncilEventViewSet(viewsets.ReadOnlyModelViewSet):
    
    serializer_class = create_generic_serializer(KLCouncilEvent)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = KLCouncilEventFilter
    search_fields = ['title', 'committee', ]
    ordering_fields = ['date',]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        today = datetime.now().date()
        return KLCouncilEvent.objects.filter(
            date__gte=today
        ).order_by('date')


class KLConstructionSiteViewSet(viewsets.ReadOnlyModelViewSet):
    
    serializer_class = create_generic_serializer(KLConstructionSite)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ConstructionSiteFilter
    search_fields = ['bez', ]
    ordering_fields = ['baustart',]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        today = now().date()
        return KLConstructionSite.objects.filter(
            bauende__gte=today
        ).order_by('baustart')


class DemographicDataViewSet(viewsets.ReadOnlyModelViewSet):
    
    serializer_class = create_generic_serializer(DemographicData)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = DemographicDataFilter
    ordering_fields = ['city_district_name',]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return DemographicData.objects.all()
    
    @action(detail=False, methods=['get'])
    def districts(self, request):
        districts = (
            DemographicData.objects
            .values('city_district_id', 'city_district_name')
            .distinct()
            .order_by('city_district_name') 
        )
        return Response({
            "districts": [
                {"id": d["city_district_id"], "name": d["city_district_name"]}
                for d in districts
            ]
        })


class GrafanaDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    
    serializer_class = create_generic_serializer(KLSensorGrafanaDashboard)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ['id',]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return KLSensorGrafanaDashboard.objects.all()