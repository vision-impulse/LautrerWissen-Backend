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
from ..mixins import FrontendURLMixin


class KLCityDistrict(BaseModel):
    VISIBLE_OBJECT_NAME = "Stadtteil"
    MAP_FIELDS = {
        "name": "Name",
        **BaseModel.MAP_FIELDS,
    }

    name = models.CharField(max_length=255)
    geometry = models.PolygonField()


class KLParkingZone(BaseModel):
    VISIBLE_OBJECT_NAME = "Parkzone"
    MAP_FIELDS = {
        "zone": "Zone",
        **BaseModel.MAP_FIELDS,
    }
    zone = models.CharField(max_length=100)
    geometry = models.PolygonField()


class KLParkingLocation(BaseModel):
    VISIBLE_OBJECT_NAME = "Parkplatz"
    MAP_FIELDS = {
        "name": "Name",
        "address": "Adresse",
        "total_spots": "Anzahl Parkplätze",
        **BaseModel.MAP_FIELDS,
    }

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    location_type = models.CharField(max_length=50)
    total_spots = models.IntegerField()
    geometry = models.PointField()


class KLVacantLot(BaseModel):
    VISIBLE_OBJECT_NAME = "Baulücke"
    MAP_FIELDS = {
        "d4u_balk_nummer": "Name",
        "link": "Link",
        "d4u_balk_art": "Art",
        "d4u_balk_flstnr": "Flurstück Nr.",
        "d4u_balk_lage": "Flurstück Name",
        **BaseModel.MAP_FIELDS,
    }

    gml_id = models.CharField(max_length=100)
    link = models.URLField()
    pgis_id = models.CharField(max_length=100, null=True, blank=True)
    d4u_balk_nummer = models.CharField(max_length=50, null=True, blank=True)
    d4u_balk_lage = models.CharField(max_length=100, null=True, blank=True)
    d4u_balk_art = models.CharField(max_length=50, null=True, blank=True)
    d4u_balk_flaeche = models.CharField(max_length=50, null=True, blank=True)
    d4u_balk_flstnr = models.CharField(max_length=50, null=True, blank=True)
    d4u_balk_stadt = models.CharField(max_length=100, null=True, blank=True)
    d4u_balk_eigent = models.CharField(max_length=50, null=True, blank=True)
    gid = models.CharField(max_length=50, null=True, blank=True)
    geometry = models.PolygonField()


class KLConstructionSite(BaseModel):
    VISIBLE_OBJECT_NAME = "Baustelle"

    MAP_FIELDS = {
        "bez": "Titel",
        "ort": "Hier sind wir vor Ort",
        "baustarttxt": "Baubeginn",
        "bauendetxt": "Bauende",
        "uml": "Umleitung",
        "anm": "Das ist unsere Aufgabe ",
        "txt": "So gehen wir vor",
        "erfasser": "Erfasser",
        "ansprech": "Ansprechpartner",
        "email": "E-Mail",
        **BaseModel.MAP_FIELDS,
    }
    
    gml_id = models.CharField(max_length=100)
    gid = models.CharField(max_length=50)
    bez = models.CharField(max_length=100)
    baustart = models.DateField(null=True, blank=True)
    baustarttxt = models.CharField(max_length=50, null=True, blank=True)
    bauende = models.DateField(null=True, blank=True)
    bauendetxt = models.CharField(max_length=50, null=True, blank=True)
    txt = models.TextField(null=True, blank=True)
    strasse = models.TextField()
    ortsteil = models.CharField(max_length=100)
    ort = models.TextField()
    anm = models.TextField(null=True, blank=True)
    ansprech = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefon = models.CharField(max_length=100, null=True, blank=True)
    uml = models.TextField(null=True, blank=True)
    erfasser = models.CharField(max_length=50, null=True, blank=True)
    erfassertxt = models.CharField(max_length=200, null=True, blank=True)
    geplant = models.TextField(null=True, blank=True)
    rw = models.IntegerField(null=True, blank=True)
    hw = models.IntegerField(null=True, blank=True)
    geox = models.FloatField()
    geoy = models.FloatField()
    pdflink = models.URLField(null=True, blank=True)
    geometry = models.PointField()


class KLLandUsePlan(BaseModel):
    VISIBLE_OBJECT_NAME = "Baurecht"
    MAP_FIELDS = {
        "baunvo": "Baunvo",
        "bez": "Bezeichnung",
        "satzung": "Satzung",
        "web": "Web",
        **BaseModel.MAP_FIELDS,
    }

    kl_id = models.CharField(max_length=100, null=True, blank=True)
    gml_id = models.CharField(max_length=100, null=True, blank=True)
    gid = models.CharField(max_length=50, null=True, blank=True)
    aufstellun = models.CharField(max_length=100, null=True, blank=True)
    baugb = models.CharField(max_length=50, null=True, blank=True)
    baunvo = models.CharField(max_length=50, null=True, blank=True)
    bez = models.CharField(max_length=200, null=True, blank=True)
    datestampe = models.CharField(max_length=100, null=True, blank=True)
    datestampn = models.CharField(max_length=100, null=True, blank=True)
    geltfl = models.CharField(max_length=50, null=True, blank=True)
    grfl = models.CharField(max_length=50, null=True, blank=True)
    nettofl = models.CharField(max_length=50, null=True, blank=True)
    nummer = models.CharField(max_length=50, null=True, blank=True)
    objid = models.CharField(max_length=100, null=True, blank=True)
    pmfkey = models.CharField(max_length=100, null=True, blank=True)
    pmfmark = models.CharField(max_length=50, null=True, blank=True)
    satzung = models.CharField(max_length=100, null=True, blank=True)
    timestampe = models.CharField(max_length=100, null=True, blank=True)
    timestampn = models.CharField(max_length=100, null=True, blank=True)
    umlegfl = models.CharField(max_length=50, null=True, blank=True)
    verkfl = models.CharField(max_length=50, null=True, blank=True)
    veroeff = models.CharField(max_length=100, null=True, blank=True)
    web = models.URLField(null=True, blank=True)
    geometry = models.GeometryField()


class KLEnvironmentalSensor(BaseModel):
    VISIBLE_OBJECT_NAME = "Umweltsensor"
    MAP_FIELDS =  {"sensor_type": "Sensor Typ",
                   "sensor_topic": "WSTOPIC",
                    "data_source": "Datenquelle",
                    "city_district_name": "Stadtteil"
                    }

    SENSOR_TYPES = [
        ('weather', 'Wetterstation'),
        ('particle', 'Luftqualität'),
        ('sound', 'Lärm'),
        ('distance_lidar', 'Distance Lidar'),
        ('distance_ultrasonic', 'Distance Ultrasonic'),
        ('temperature', 'Temperatur'),
        ('moisture', 'Feuchtigkeit'),
        ('particle_temp', 'Luftqualität & Temperatur'),
        ('temperature_multi', 'Temperatur'),
    ]
    sensor_topic = models.CharField(max_length=255)
    sensor_type = models.CharField(max_length=50, choices=SENSOR_TYPES)
    geometry = models.GeometryField(null=True, blank=True)


class KLSculpture(BaseModel):
    VISIBLE_OBJECT_NAME = "Skulptur"
    MAP_FIELDS =  {"name": "Name",
                   "artist": "Künstler",
                   "year_created": "Entstehungsjahr",
                   "source": "Quelle",
                   "category": "Kategorie",
                   "location_name": "Ort",
                   "photo_url": "Bild (URL)",
                   **BaseModel.MAP_FIELDS,
                   }

    gml_id = models.CharField(max_length=255, unique=False)
    gid = models.CharField(max_length=255, unique=False)
    photo_url = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    artist = models.CharField(max_length=255, blank=True, null=True)
    year_created = models.CharField(max_length=255, blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    location_name = models.CharField(max_length=255)
    geometry = models.GeometryField()


class KLEducationalInstitution(BaseModel):
    VISIBLE_OBJECT_NAME = "Bildungseinrichtung"
    MAP_FIELDS =  {"name": "Name",
                   "education_type": "Kategorie",
                   "education_subtype": "Unterkategorie",
                   "extended_name": "Vollst. Name",
                   "address": "Address",
                   "postal_code": "PLZ",
                   "city": "Ort",
                   "website_url": "Webseite",
                   **BaseModel.MAP_FIELDS,
                   }

    gml_id = models.CharField(max_length=255, unique=False)
    gid = models.CharField(max_length=255, unique=False)
    education_type = models.CharField(max_length=255)
    education_subtype = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    extended_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    geometry = models.GeometryField()


class KLSensorGrafanaDashboard(BaseModel, FrontendURLMixin):
    VISIBLE_OBJECT_NAME = "Sensor Dashboard"
    MAP_FIELDS =  {"name": "Name",
                   "size_radius_meters": "size_radius_meters",
                   "dashboard_url": "dashboard_url",
                   "timefilters": "timefilters",
                   **BaseModel.MAP_FIELDS,
                   }

    name = models.CharField(max_length=100)
    dashboard_url = models.URLField()
    geometry = models.GeometryField()
    size_radius_meters = models.FloatField()
    timefilters = models.CharField(max_length=100)


class KLFieldtestMeasurements(BaseModel):

    MAP_FIELDS =  {"rssi": "RSSI",
                   "invalid": "invalid",
                   "created_at": "created_at",
                   **BaseModel.MAP_FIELDS,
                   }
    time = models.BigIntegerField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    sats = models.IntegerField(blank=True, null=True)
    battery = models.IntegerField(blank=True, null=True)
    triggered = models.CharField(max_length=50, blank=True, null=True)
    rssi = models.FloatField(blank=True, null=True)
    snr = models.FloatField(blank=True, null=True)
    uplink = models.IntegerField(blank=True, null=True)
    downlink = models.IntegerField(blank=True, null=True)
    invalid = models.IntegerField(blank=True, null=True)
    payloadHex = models.CharField(max_length=255, blank=True, null=True)
    rawdata = models.TextField(blank=True, null=True)
    deveui = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
