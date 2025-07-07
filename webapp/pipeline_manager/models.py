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
 
from django.db import models

from enum import Enum

class PipelineType(Enum):
    KL_EVENTS = "Veranstaltungen (MIADI) Import"
    WGA_EVENTS = "Veranstaltungen (Was Geht App?) Import"
    KL_EVENTS_RIS = "Ratsveranstaltungen (RSS) Import"
    KL_GEO_WFS = "Geodaten WFS Import"
    KL_GEO_RESOURCES = "Geodaten Import"
    KL_SENSOR_RESOURCES = "Sensor (MQTT) Import"
    WIFI_FREIFUNK = "Wifi Freifunk Import"
    WIFI_LOCAL = "Wifi (lokale Daten) Import"
    EV_STATIONS = "E-Ladestationen Import"
    VRN = "VRN Haltestellen Import"
    OSM = "Open Street Map Import"
    WIKIPEDIA = "Wikipedia Import"
    EMERGENCY_POINTS = "Rettungspunkte Import"
    TTN_GATEWAY = "TTN Gateway Import"


# Pipeline model to manage each pipeline
class Pipeline(models.Model):
    PIPELINE_CHOICES = [(pt.name, pt.value) for pt in PipelineType]
    name = models.CharField(max_length=100, choices=PIPELINE_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)

class BaseResource(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='resources', null=True)
    data_source = models.CharField(max_length=255)
    db_model_class = models.CharField(max_length=255)
    class Meta:
        abstract = True  # Not a real DB table

class LocalResourceFile(BaseResource):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='local_resources', null=True)
    filename = models.CharField(max_length=255)

class RemoteResourceFile(BaseResource):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='remote_resources', null=True)
    filename = models.CharField(max_length=255)
    url = models.URLField()

class ResourceOSM(BaseResource):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='osm_resources', null=True)
    tags = models.JSONField(default=dict)
    filename = models.CharField(max_length=255)

class ResourceWFSFile(BaseResource):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='wfs_resources', null=True)
    url = models.URLField()
    srs_name = models.CharField(max_length=100)
    layer_name = models.CharField(max_length=100)
    out_format = models.CharField(max_length=50)
    filename = models.CharField(max_length=255)

class ResourceWikipage(BaseResource):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='wikipage_resources')
    page_name = models.CharField(max_length=255)
    table_indices = models.JSONField(default=list)
    table_filenames = models.JSONField(default=list)
    table_extractor_classes = models.JSONField(default=list)