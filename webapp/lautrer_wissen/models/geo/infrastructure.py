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


class EmergencyPoint(BaseModel):
    VISIBLE_OBJECT_NAME = "Rettungspunkt"
    MAP_FIELDS = {
        "rp_nr": "Nr. des Rettungspunktes",
        "description": "Beschreibung der Lage",
        "information_sign": "Informationsschild",
        "originator": "Urheber",
        **BaseModel.MAP_FIELDS,
    }

    id = models.AutoField(primary_key=True)
    geometry = models.PointField(verbose_name="Location")

    rp_nr = models.CharField(max_length=255, verbose_name="RP NR")
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    information_sign = models.CharField(max_length=255, verbose_name="Info Sign", null=True, blank=True)
    originator = models.CharField(max_length=255, verbose_name="Originator", null=True, blank=True)
    federal_state = models.CharField(max_length=255, verbose_name="Federal state")


class VRNBusStation(BaseModel):
    VISIBLE_OBJECT_NAME = "Haltestelle (Bus)"
    MAP_FIELDS = {
        "name": "Name",
        "station_number": "Haltestellennummer",
        "direction": "Richtung",
        "lines": "Linien",
        "seating": "Sitzgelegenheit",
        "waste_bin": "Abfallbehaelter",
        "lighting": "Beleuchtung",
        **BaseModel.MAP_FIELDS,
    }

    global_id = models.CharField(max_length=255, verbose_name="Global ID")
    name = models.CharField(max_length=255, null=True, verbose_name="Name")
    platform_global_id = models.CharField(max_length=255, verbose_name="Platform Global ID")
    geometry = models.PointField(verbose_name="Location")
    station_number = models.IntegerField(verbose_name="Station Number")
    direction = models.TextField(verbose_name="Direction")
    lines = models.TextField(verbose_name="Lines")
    seating = models.CharField(max_length=4, verbose_name="Seating Availability")
    waste_bin = models.CharField(max_length=4, verbose_name="Waste Bin Availability")
    lighting = models.CharField(max_length=4, verbose_name="Lighting Availability")

    def __str__(self):
        return f"BusStation {self.station_number} - {self.global_id}"


class WLANHotspot(BaseModel):
    VISIBLE_OBJECT_NAME = "WIFI-Hotspot"
    MAP_FIELDS = {
        "name": "Name",
        "description": "Beschreibung",
        **BaseModel.MAP_FIELDS,
    }

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    geometry = models.GeometryField()


class ChargingStation(BaseModel):
    VISIBLE_OBJECT_NAME = "E-Ladestation"
    MAP_FIELDS = {
        "operator": "Betreiber",
        "commissioning_date": "Datum der Inbetriebnahme",
        "num_charging_points": "Anzahl Ladesäulen",
        **BaseModel.MAP_FIELDS,
    }
    for idx in range(6):
        MAP_FIELDS[f"socket_type_{idx+1}"] = f"{idx+1}. Ladesäule Steckdosentyp"
        MAP_FIELDS[f"power_output_{idx + 1}"] = f"{idx+1}. Ladesäule Leistungsabgabe"

    geometry = models.GeometryField(null=True)
    operator = models.CharField(max_length=255, blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    house_number = models.CharField(max_length=50, blank=True, null=True)
    address_addition = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    commissioning_date = models.DateField()
    nominal_power = models.DecimalField(max_digits=10, decimal_places=2)  # kW
    charging_type = models.CharField(max_length=255)

    num_charging_points = models.PositiveIntegerField()
    socket_type_1 = models.CharField(max_length=255, blank=True, null=True)
    power_output_1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # kW
    public_key_1 = models.TextField(blank=True, null=True)
    socket_type_2 = models.CharField(max_length=255, blank=True, null=True)
    power_output_2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # kW
    public_key_2 = models.TextField(blank=True, null=True)
    socket_type_3 = models.CharField(max_length=255, blank=True, null=True)
    power_output_3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # kW
    public_key_3 = models.TextField(blank=True, null=True)
    socket_type_4 = models.CharField(max_length=255, blank=True, null=True)
    power_output_4 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # kW
    public_key_4 = models.TextField(blank=True, null=True)
    socket_type_5 = models.CharField(max_length=255, blank=True, null=True)
    power_output_5 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # kW
    public_key_5 = models.TextField(blank=True, null=True)
    socket_type_6 = models.CharField(max_length=255, blank=True, null=True)
    power_output_6 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # kW
    public_key_6 = models.TextField(blank=True, null=True)


class TTNGateway(BaseModel):
    VISIBLE_OBJECT_NAME = "TTN Gateway"
    MAP_FIELDS =  {"eui": "EUI",
                   "net_id": "NetID",
                   "tenant_id": "TenantId",
                   "cluster_id": "ClusterId",
                   "antenna_count": "Anzahl Antennen",
                   "online": "Status",
                   **BaseModel.MAP_FIELDS,
                   }
    gateway_id = models.CharField(max_length=255, blank=True, null=True)  
    net_id = models.CharField(max_length=32)
    tenant_id = models.CharField(max_length=64)
    eui = models.CharField(max_length=32)
    cluster_id = models.CharField(max_length=128)
    updated_at = models.DateTimeField()
    geometry = models.GeometryField()
    antenna_placement = models.CharField(max_length=255, blank=True, null=True) 
    antenna_count = models.PositiveIntegerField()
    online = models.BooleanField()

