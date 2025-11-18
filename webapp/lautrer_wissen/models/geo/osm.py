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

from django.contrib.gis.db import models
from ..base_model import BaseModel


class OsmBaseLocation(BaseModel):
    geometry = models.GeometryField(null=True, blank=True)
    
    class Meta:
        abstract = True


class OsmBaseLocationNamed(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)

    class Meta:
        abstract = True


class OsmAdvertisingColumn(OsmBaseLocation):
    VISIBLE_OBJECT_NAME = "Litfaßsäule"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmVolleyball(OsmBaseLocation):
    VISIBLE_OBJECT_NAME = "Volleyballfeld"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmVendingMachineDogToilet(OsmBaseLocation):
    VISIBLE_OBJECT_NAME = "Hundekotbeutel"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OSMAmenityBench(OsmBaseLocation):
    VISIBLE_OBJECT_NAME = "Sitzbank"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmCemetery(OsmBaseLocationNamed):
    VISIBLE_OBJECT_NAME = "Friedhof"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmCinema(OsmBaseLocationNamed):
    VISIBLE_OBJECT_NAME = "Kino"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmCopyshop(OsmBaseLocationNamed):
    VISIBLE_OBJECT_NAME = "Kopiershop"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmZoo(OsmBaseLocationNamed):
    VISIBLE_OBJECT_NAME = "Zoo"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmEscapegame(OsmBaseLocationNamed):
    VISIBLE_OBJECT_NAME = "Escape-Room"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmMiniatureGolf(OsmBaseLocationNamed):
    VISIBLE_OBJECT_NAME = "Minigolf"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmMusicSchool(OsmBaseLocationNamed):
    VISIBLE_OBJECT_NAME = "Musikschule"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmDrivingSchool(OsmBaseLocationNamed):
    VISIBLE_OBJECT_NAME = "Fahrschule"
    MAP_FIELDS = BaseModel.MAP_FIELDS


class OsmNaturalTrees(BaseModel):
    VISIBLE_OBJECT_NAME = "Baum"
    MAP_FIELDS = {
        "genus_de": "Baumgattung",
        "species": "Baumart",
        **BaseModel.MAP_FIELDS, 
    }
    name = models.CharField(max_length=255, null=True, blank=True)
    genus = models.CharField(max_length=255, null=True, blank=True)
    genus_de = models.CharField(max_length=255, null=True, blank=True)
    leaf_cycle = models.CharField(max_length=255, null=True, blank=True)
    leaf_type = models.CharField(max_length=255, null=True, blank=True)
    diameter_crown = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    natural_protection = models.CharField(max_length=255, null=True, blank=True)
    species = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    genus_en = models.CharField(max_length=255, null=True, blank=True)
    species_de = models.CharField(max_length=255, null=True, blank=True)
    diameter = models.TextField(null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmLeisurePlayground(BaseModel):
    VISIBLE_OBJECT_NAME = "Spielplatz"
    MAP_FIELDS = {
        "name": "Name",
        "operator": "Betreiber",
        **BaseModel.MAP_FIELDS, 
    }
    access = models.CharField(max_length=255, null=True, blank=True)
    leisure = models.CharField(max_length=255, null=True, blank=True)
    wheelchair = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    max_age = models.CharField(max_length=255, null=True, blank=True)
    opening_hours = models.CharField(max_length=255, null=True, blank=True)
    sport = models.CharField(max_length=255, null=True, blank=True)
    playground = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField()


class OsmLeisurePitch(BaseModel):
    VISIBLE_OBJECT_NAME = "Freizeitplatz"
    MAP_FIELDS = {
        "name": "Name",
        "description": "Beschreibung",
        "operator": "Betreiber",
        **BaseModel.MAP_FIELDS, 
    }
    access = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField()


class OsmSportTennis(BaseModel):
    VISIBLE_OBJECT_NAME = "Tennisplatz"
    MAP_FIELDS = {
        "name": "Name",
        **BaseModel.MAP_FIELDS, 
    }
    name = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField()


class OsmSportSoccer(BaseModel):
    VISIBLE_OBJECT_NAME = "Fußballplatz"
    MAP_FIELDS = {
        "name": "Name",
        "website": "Website",
        **BaseModel.MAP_FIELDS, 
    }
    name = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    name_de = models.CharField(max_length=255, null=True, blank=True)
    access = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField()


class OsmSportBasketball(BaseModel):
    VISIBLE_OBJECT_NAME = "Basketballplatz"
    MAP_FIELDS = {
        "name": "Name",
        **BaseModel.MAP_FIELDS, 
    }
    sport = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField()


class OsmAmenityToilets(BaseModel):
    VISIBLE_OBJECT_NAME = "Öffentliche Toilette"
    MAP_FIELDS = {
        "opening_hours": "Öffnungszeiten",
        "operator": "Betreiber",
        "description": "Barrierefreiheit",
        "access": "Zugang",
        "fee": "Gebühr",
        **BaseModel.MAP_FIELDS, 
    }
    access = models.CharField(max_length=255, null=True, blank=True)
    fee = models.CharField(max_length=255, null=True, blank=True)
    payment_coins = models.CharField(max_length=255, null=True, blank=True)
    payment_notes = models.CharField(max_length=255, null=True, blank=True)
    toilets_disposal = models.CharField(max_length=255, null=True, blank=True)
    toilets_position = models.CharField(max_length=255, null=True, blank=True)
    unisex = models.CharField(max_length=255, null=True, blank=True)
    wheelchair = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    brand_wikidata = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    opening_hours = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField()


class OsmAmenityWasteBasket(BaseModel):
    VISIBLE_OBJECT_NAME = "Abfalleimer"
    MAP_FIELDS = {
        "data_source": "Datenquelle",
        "data_acquisition_date": "Datenstand"
    }
    waste_basket_count = models.IntegerField(null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmAmenityDrinkingWater(BaseModel):
    VISIBLE_OBJECT_NAME = "Wasserspender (Trinkwasser)"
    MAP_FIELDS = {
        "data_source": "Datenquelle",
        "data_acquisition_date": "Datenstand"
    }
    fee = models.CharField(max_length=255, null=True, blank=True)
    fountain = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmParcelLocker(BaseModel):
    VISIBLE_OBJECT_NAME = "Packetstation"
    MAP_FIELDS = {
        "operator": "Betreiber",
        "parcel_mail_in": "Pakete verschicken",
        "parcel_pickup": "Pakete abholen",
        "postal_code": "Postleitzahl",
        **BaseModel.MAP_FIELDS, 
    }
    brand = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    parcel_mail_in = models.CharField(max_length=255, null=True, blank=True)
    parcel_pickup = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    locker_type = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmPostBox(BaseModel):
    VISIBLE_OBJECT_NAME = "Briefkasten"
    MAP_FIELDS = {
        "operator": "Betreiber",
        "collection_times": "Leerung",
        **BaseModel.MAP_FIELDS, 
    }
    collection_times = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmBicycleRental(BaseModel):
    VISIBLE_OBJECT_NAME = "Fahrradvermietung"
    MAP_FIELDS = {
        "name": "Name",
        "brand": "Marke",
        "operator": "Betreiber",
        "capacity": "Kapazität",
        **BaseModel.MAP_FIELDS, 
    }
    brand = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    capacity = models.CharField(max_length=255, null=True, blank=True)
    network = models.CharField(max_length=255, null=True, blank=True)
    bicycle_rental = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmCarRental(BaseModel):
    VISIBLE_OBJECT_NAME = "Autovermietung"
    MAP_FIELDS = {
        "name": "Name",
        **BaseModel.MAP_FIELDS, 
    }
    brand = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmBicycleRepairStation(BaseModel):
    VISIBLE_OBJECT_NAME = "Fahrradreparatur-Station"
    MAP_FIELDS = {
        "service_bicycle_pump": "Pumpe vorhanden",
        "service_bicycle_stand": "Stand vorhanden",
        "service_bicycle_tools": "Werkzeug vorhanden",
        "service_bicycle_chain_tool": "Kettenwerkzeug vorhanden",
        "valves": "Ventile",
        **BaseModel.MAP_FIELDS, 
    }
    service_bicycle_pump = models.CharField(max_length=255, null=True, blank=True)
    service_bicycle_stand = models.CharField(max_length=255, null=True, blank=True)
    service_bicycle_tools = models.CharField(max_length=255, null=True, blank=True)
    service_bicycle_chain_tool = models.CharField(max_length=255, null=True, blank=True)
    valves = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmRecyclingContainer(BaseModel):
    VISIBLE_OBJECT_NAME = "Recycling-Container"
    MAP_FIELDS = {
        "operator": "Betreiber",
        "recycling_glass_bottles": "Glasflaschen",
        "recycling_clothes": "Kleider",
        "recycling_shoes": "Schuhe",
        **BaseModel.MAP_FIELDS, 
    }
    recycling_glass = models.CharField(max_length=255, null=True, blank=True)
    recycling_glass_bottles = models.CharField(max_length=255, null=True, blank=True)
    recycling_type = models.CharField(max_length=255, null=True, blank=True)
    recycling_clothes = models.CharField(max_length=255, null=True, blank=True)
    recycling_shoes = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmRecyclingCenter(BaseModel):
    VISIBLE_OBJECT_NAME = "Wertstoffhof"
    MAP_FIELDS = {
        "name": "Name",
        "operator": "Betreiber",
        "opening_hours": "Öffnungszeiten",
        "description": "Beschreibung",
        "addr_street": "Straße",
        "addr_housenumber": "Hausnummer",
        "addr_postcode": "Postleitzahl",
        **BaseModel.MAP_FIELDS, 
    }
    operator = models.CharField(max_length=255, null=True, blank=True)
    opening_hours = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    recycling_type = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    addr_city = models.CharField(max_length=255, null=True, blank=True)
    addr_housenumber = models.CharField(max_length=255, null=True, blank=True)
    addr_postcode = models.CharField(max_length=255, null=True, blank=True)
    addr_street = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmBicycleParking(BaseModel):
    VISIBLE_OBJECT_NAME = "Fahrradabstellfläche"
    MAP_FIELDS = {
        "capacity": "Kapazität",
        "covered": "Überdacht",
        "fee": "Gebühr",
        **BaseModel.MAP_FIELDS, 
    }
    bicycle_parking = models.CharField(max_length=255, null=True, blank=True)
    capacity = models.CharField(max_length=255, null=True, blank=True)
    covered = models.CharField(max_length=255, null=True, blank=True)
    fee = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmAmenityParking(BaseModel):
    VISIBLE_OBJECT_NAME = "Parkplatz"
    MAP_FIELDS = {
        "access": "Zugang",
        "capacity_disabled": "Kapazität Behindertenparkplätze",
        "wheelchair": "Barrierefrei",
        **BaseModel.MAP_FIELDS, 
    }
    access = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    wheelchair = models.CharField(max_length=255, null=True, blank=True)
    fee = models.CharField(max_length=255, null=True, blank=True)
    capacity_disabled = models.CharField(max_length=255, null=True, blank=True)
    building = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmLeisureDance(BaseModel):
    VISIBLE_OBJECT_NAME = "Tanzschule"
    MAP_FIELDS = {
        "name": "Name",
        "contact_webseite": "Webseite",
        **BaseModel.MAP_FIELDS, 
    }
    name = models.CharField(max_length=255, null=True, blank=True)
    dance_teaching = models.CharField(max_length=10, null=True, blank=True)
    contact_webseite = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmNatureReserve(BaseModel):
    VISIBLE_OBJECT_NAME = "Naturschutzgebiet"
    MAP_FIELDS = {
        "name": "Name",
        **BaseModel.MAP_FIELDS, 
    }
    name = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmVendingMachineParkingTicket(BaseModel):
    VISIBLE_OBJECT_NAME = "Parkscheinautomat"
    MAP_FIELDS = {
        "name": "Name",
        **BaseModel.MAP_FIELDS, 
    }
    name = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmSportCenterSwimming(BaseModel):
    VISIBLE_OBJECT_NAME = "Schwimmbad"
    MAP_FIELDS = {
        "name": "Name",
        **BaseModel.MAP_FIELDS, 
    }
    sport = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmSportCenterClimbing(BaseModel):
    VISIBLE_OBJECT_NAME = "Kletterhalle"
    MAP_FIELDS = {
        "name": "Name",
        "website": "Website",
        **BaseModel.MAP_FIELDS, 
    }
    sport = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmLandUseMilitary(BaseModel):
    VISIBLE_OBJECT_NAME = "Militärfläche"
    MAP_FIELDS = {
        "name": "Name",
        **BaseModel.MAP_FIELDS, 
    }
    name = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)


class OsmLeisureDogPark(BaseModel):
    VISIBLE_OBJECT_NAME = "Hundewiese"
    MAP_FIELDS = {
        "name": "Name",
        "website": "Website",
        **BaseModel.MAP_FIELDS, 
    }
    name = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField(null=True, blank=True)
