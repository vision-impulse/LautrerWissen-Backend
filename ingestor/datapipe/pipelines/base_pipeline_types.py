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
class LocalResourceFile(BaseResource):
    """Represents simple file-based resources."""
    filename: str


@dataclass
class RemoteResourceFile(BaseResource):
    """Represents simple file-based resources."""
    url: str
    filename: str


@dataclass
class ResourceOSM(BaseResource):
    """Represents an OSM resource with specific attributes."""
    tags: Dict[str, str] 
    filename: str


@dataclass
class ResourceWFSFile(BaseResource):
    """Represents a WFS resource with additional spatial attributes."""
    url: str
    srs_name: str
    layer_name: str
    out_format: str
    filename: str


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
    KL_GEO_WFS = "kl_wfs_pipeline"
    KL_SENSOR_RESOURCES = "kl_sensors_mqtt_pipeline"
    EMERGENCY_POINTS = "emergency_point_pipeline"
    EV_STATIONS = "ev_pipeline"
    KL_EVENTS = "kl_event_calendar_pipeline"
    KL_EVENTS_RIS = "kl_event_ris_calendar_pipeline"
    KL_GEO_RESOURCES = "kl_geo_pipeline"
    WIFI_FREIFUNK = "wifi_freifunk_pipeline"
    WIFI_LOCAL = "wifi_myspot_empera_pipeline"
    WGA_EVENTS = "was_geht_app_pipeline"
    TTN_GATEWAY = "ttn_gateway_pipeline"
    VRN = "vrn_pipeline"


PIPELINE_RESOURCE_MAP = {
    PipelineType.KL_GEO_WFS: ResourceWFSFile,
    PipelineType.WIKIPEDIA: ResourceWikipage,
    PipelineType.KL_SENSOR_RESOURCES: LocalResourceFile,
    PipelineType.EMERGENCY_POINTS: RemoteResourceFile,
    PipelineType.EV_STATIONS: RemoteResourceFile,
    PipelineType.KL_EVENTS: RemoteResourceFile,
    PipelineType.KL_EVENTS_RIS:RemoteResourceFile,
    PipelineType.KL_GEO_RESOURCES: RemoteResourceFile,
    PipelineType.WIFI_FREIFUNK: RemoteResourceFile,
    PipelineType.WGA_EVENTS: RemoteResourceFile,
    PipelineType.TTN_GATEWAY: RemoteResourceFile,
    PipelineType.VRN: RemoteResourceFile,
    PipelineType.WIFI_LOCAL: LocalResourceFile,
    PipelineType.OSM: ResourceOSM
}
