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

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.viewset_generic import create_generic_viewset
from .views.viewset_geo import create_geo_viewset
from .views.viewset_wiki import create_wiki_viewset
from .views.viewset_events import KLLeisureEventViewSet, KLWGAEventViewSet
from .views.viewset_events import KLCouncilEventViewSet, KLConstructionSiteViewSet
from .views.viewset_events import DemographicDataViewSet, DemographicDataDistrictsViewSet
from .views.viewset_elections import ElectionViewSet, ElectionResultViewSet
from .models.events import events
from .models import API_GEO_MODELS, API_WIKI_MODLES

router = DefaultRouter()

# Dynamically create and register viewset for each geomodel
for model in API_GEO_MODELS:
    router.register(f"geo/{model.__name__.lower()}", create_geo_viewset(model), basename=f"{model.__name__.lower()}-geo")

# Dynamically create and register viewset for each wiki model
for model in API_WIKI_MODLES:
    router.register(f"wiki/{model.__name__.lower()}", create_wiki_viewset(model), basename=f"{model.__name__.lower()}")

# Create and register viewset for election results
router.register(r'elections', ElectionViewSet, basename='election')
router.register(r'election_results', ElectionResultViewSet, basename='election-result')

# Create and register viewset for each event
router.register(r"events/leisure", KLLeisureEventViewSet, basename='leisureevent')
router.register(r"events/council", KLCouncilEventViewSet, basename='councilevent')
router.register(r"events/wga", KLWGAEventViewSet, basename='wgaevent')

# Create and register viewset for construction sites
router.register(r'construction-sites', KLConstructionSiteViewSet, basename='construction-site')

# Create and register viewset for demographics
router.register(r'demographics', DemographicDataViewSet, basename='demographics')

