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

import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Type
from enum import Enum
from ingestor.datapipe.pipelines.base_pipeline import PipelineType



@dataclass
class BaseResource:
    """Base class for all resources, containing common attributes."""
    data_source: str
    db_model_class: str


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
    tags: Dict[str, str] #dict
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
    page_name: str
    table_indices: list
    table_filenames: list
    table_extractor_classes: list


@dataclass
class Config:
    out_dir: str
    pipelines: Dict[PipelineType, List[BaseResource]] = field(default_factory=dict)

    def get_resources(self, source_type: PipelineType):
        return self.resources.get(source_type, [])


def load_config(file_path: str) -> Config:
    """Loads pipeline configurations from YAML."""
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    return Config(
        out_dir=data["out_dir"],
        pipelines={
            PipelineType.OSM: [ResourceOSM(**res) for res in data.get("osm_resources", [])],
            PipelineType.KL_GEO_WFS: [ResourceWFSFile(**res) for res in data.get("kl_wfs_resources", [])],
            PipelineType.WIKIPEDIA: [ResourceWikipage(**res) for res in data.get("wiki_resources", [])],
            PipelineType.KL_SENSOR_RESOURCES: [LocalResourceFile(**res) for res in data.get("kl_sensors_mqtt", [])],
            PipelineType.EMERGENCY_POINTS: [RemoteResourceFile(**res) for res in data.get("emergency_point_resources", [])],
            PipelineType.EV_STATIONS: [RemoteResourceFile(**res) for res in data.get("ev_resource", [])],
            PipelineType.KL_EVENTS: [RemoteResourceFile(**res) for res in data.get("kl_event_calendar_resource", [])],
            PipelineType.KL_EVENTS_RIS: [RemoteResourceFile(**res) for res in data.get("kl_event_ris_calendar_resource", [])],
            PipelineType.KL_GEO_RESOURCES: [RemoteResourceFile(**res) for res in data.get("kl_geo_resources", [])],
            PipelineType.VRN: [RemoteResourceFile(**res) for res in data.get("vrn_resource", [])],
            PipelineType.WIFI_FREIFUNK: [RemoteResourceFile(**res) for res in data.get("wifi_freifunk_resource", [])],
            PipelineType.WGA_EVENTS: [RemoteResourceFile(**res) for res in data.get("was_geht_app_resources", [])],
            PipelineType.TTN_GATEWAY: [RemoteResourceFile(**res) for res in data.get("ttn_gateway_resource", [])],
            PipelineType.WIFI_LOCAL: [LocalResourceFile(**res) for res in data.get("wifi_myspot_empera_resource", [])],
        },
    )