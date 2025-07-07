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

from .geo.infrastructure import *
from .geo.kl import *
from .geo.osm import *
from .geo.wikipedia import *
from .events.events import *
from .elections.election_results import *
from .demographics.demographic_data import *

from .geo import osm, wikipedia, kl, infrastructure

API_GEO_MODELS = [
    osm.OsmLeisurePlayground, osm.OsmLeisurePitch, osm.OsmSportTennis, osm.OsmSportBasketball,
    osm.OsmSportSoccer, osm.OsmAmenityToilets, osm.OsmAmenityWasteBasket, osm.OSMAmenityBench,
    osm.OsmAmenityDrinkingWater, osm.OsmNaturalTrees,

    osm.OsmRecyclingContainer, osm.OsmRecyclingCenter,
    osm.OsmSportCenterClimbing, osm.OsmSportCenterSwimming, osm.OsmVolleyball, osm.OsmNatureReserve,
    osm.OsmVendingMachineDogToilet, osm.OsmVendingMachineParkingTicket, osm.OsmAdvertisingColumn,
    osm.OsmLeisureDance, osm.OsmDrivingSchool, osm.OsmMusicSchool, osm.OsmMiniatureGolf, osm.OsmEscapegame,
    osm.OsmZoo, osm.OsmCopyshop, osm.OsmCinema, osm.OsmCemetery, osm.OsmAmenityParking, osm.OsmBicycleParking,
    osm.OsmBicycleRepairStation, osm.OsmCarRental, osm.OsmBicycleRental, osm.OsmPostBox, osm.OsmParcelLocker,

    infrastructure.ChargingStation, infrastructure.VRNBusStation, infrastructure.WLANHotspot,
    infrastructure.EmergencyPoint, infrastructure.TTNGateway,

    kl.KLVacantLot, kl.KLParkingZone, kl.KLParkingLocation, kl.KLConstructionSite,
    kl.KLLandUsePlan, kl.KLEnvironmentalSensor, kl.KLCityDistrict, kl.KLSculpture, kl.KLEducationalInstitution, 
    kl.KLFieldtestMeasurements, kl.KLSensorGrafanaDashboard,
]

API_WIKI_MODLES = [
    wikipedia.WikiFishSculpture, wikipedia.WikiFountain, wikipedia.WikiCulturalMonument,
    wikipedia.WikiNaturalMonument, wikipedia.WikiBrewery, wikipedia.WikiNaturalReserve,
    wikipedia.WikiRitterstein, wikipedia.WikiSacralBuilding, wikipedia.WikiStolperstein
]

API_GEO_MODELS.extend(API_WIKI_MODLES)

MODELS_WITH_DETAIL_PAGE = [
    WikiFishSculpture,
    WikiFountain,
    WikiCulturalMonument,
    WikiNaturalMonument,
    WikiBrewery,
    WikiNaturalReserve,
    WikiRitterstein,
    WikiSacralBuilding,
    WikiStolperstein
]
