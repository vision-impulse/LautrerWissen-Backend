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
class PipelineConfig:
    description: str
    resources: List[BaseResource]

@dataclass
class Config:
    out_dir: str
    pipelines: Dict[PipelineType, PipelineConfig] = field(default_factory=dict)


RESOURCE_CLASS_MAP = {
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

def load_config(file_path: str) -> Config:
    """Loads pipeline configurations from YAML."""
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    out_dir=data["out_dir"]
    pipelines: Dict[PipelineType, PipelineConfig] = {}

    for pipeline_type in PipelineType:
        section = data.get(pipeline_type.value)
        if not section:
            continue  # skip missing pipelines

        description = section.get("description", "")
        resources_data = section.get("endpoints", [])

        # Select resource class dynamically based on type
        resource_cls = RESOURCE_CLASS_MAP.get(pipeline_type)
        if not resource_cls:
            continue
        resources = [resource_cls(**res) for res in resources_data]
        pipelines[pipeline_type] = PipelineConfig(description=description, resources=resources)

    return Config(out_dir=out_dir, pipelines=pipelines)
