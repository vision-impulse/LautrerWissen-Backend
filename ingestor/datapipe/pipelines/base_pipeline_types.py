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

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Type, Optional


@dataclass(kw_only=True)
class BaseResource:
    """Base class for all resources, containing common attributes."""
    data_source: str
    db_model_class: str
    db_model_class_type: Optional[str] = None  


@dataclass
class RemoteResourceFile(BaseResource):
    """Represents simple resource for remote files."""
    url: str
    filename: str
    local_path: Optional[str] = None


@dataclass(kw_only=True)
class WGAResourceFile(RemoteResourceFile):
    """Represents a resource for WGA data."""
    region_latitude: str
    region_longitude: str
    region_region: str


@dataclass(kw_only=True)
class VRNResourceFile(RemoteResourceFile):
    """Represents a resource for VRN data."""
    source_filename: str


@dataclass(kw_only=True)
class EVResourceFile(RemoteResourceFile):
    """Represents a resource for EV data."""
    city_filter: list


@dataclass(kw_only=True)
class EmergencyPointResourceFile(RemoteResourceFile):
    """Represents a resource for emergency points."""
    source_filename: str
    region_filter: str 


@dataclass
class ResourceOSM(BaseResource):
    """Represents an OSM resource with specific attributes."""
    tags: Dict[str, str] 
    filename: str
    place_filter: str


@dataclass
class ResourceWFSFile(BaseResource):
    """Represents a WFS resource with additional spatial attributes."""
    url: str
    srs_name: str
    layer_name: str
    out_format: str
    filename: str
    version: str


@dataclass
class ResourceWikipage(BaseResource):
    """Represents a wikipedia resource with specific attributes."""
    page_name: str
    table_indices: list
    table_filenames: list
    table_extractor_classes: list


class PipelineType(Enum):
    OSM = "osm_pipeline"
    WIKIPEDIA = "wiki_pipeline"
    GEO_WFS = "kl_wfs_pipeline"
    MQTT_SENSOR_RESOURCES = "kl_sensors_mqtt_pipeline"
    EMERGENCY_POINTS = "emergency_point_pipeline"
    EV_STATIONS = "ev_pipeline"
    EXTERNAL_GEO_RESOURCES = "kl_geo_pipeline"
    EVENTS_MIADI = "kl_event_calendar_pipeline"
    EVENTS_RIS = "kl_event_ris_calendar_pipeline"
    EVENTS_WGA = "was_geht_app_pipeline"
    WIFI_FREIFUNK = "wifi_freifunk_pipeline"
    WIFI_LOCAL = "wifi_myspot_empera_pipeline"
    TTN_GATEWAY = "ttn_gateway_pipeline"
    VRN = "vrn_pipeline"
    DEMOGRAPHICS = "demographics_pipeline"


PIPELINE_RESOURCE_MAP = {
    PipelineType.GEO_WFS: ResourceWFSFile,
    PipelineType.WIKIPEDIA: ResourceWikipage,
    PipelineType.MQTT_SENSOR_RESOURCES: RemoteResourceFile,
    PipelineType.EMERGENCY_POINTS: EmergencyPointResourceFile,
    PipelineType.EV_STATIONS: EVResourceFile,
    PipelineType.EVENTS_MIADI: RemoteResourceFile,
    PipelineType.EVENTS_RIS:RemoteResourceFile,
    PipelineType.EXTERNAL_GEO_RESOURCES: RemoteResourceFile,
    PipelineType.WIFI_FREIFUNK: RemoteResourceFile,
    PipelineType.EVENTS_WGA: WGAResourceFile,
    PipelineType.TTN_GATEWAY: RemoteResourceFile,
    PipelineType.VRN: VRNResourceFile,
    PipelineType.WIFI_LOCAL: RemoteResourceFile,
    PipelineType.OSM: ResourceOSM,
    PipelineType.DEMOGRAPHICS: RemoteResourceFile,
}
