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

from ingestor.datapipe.pipelines.osm_pipeline import OSMPipeline
from ingestor.datapipe.pipelines.evstation_pipeline import EVStationPipeline
from ingestor.datapipe.pipelines.kl_wfs_pipeline import WFSPipeline
from ingestor.datapipe.pipelines.kl_events_pipeline import KLEventsPipeline
from ingestor.datapipe.pipelines.kl_ris_pipeline import KLRisEventsPipeline
from ingestor.datapipe.pipelines.kl_geo_pipeline import KLGeoResourcePipeline
from ingestor.datapipe.pipelines.kl_sensors_pipeline import KLSensorsPipeline
from ingestor.datapipe.pipelines.vrn_pipeline import VRNPipeline
from ingestor.datapipe.pipelines.wiki_pipeline import WikipediaPipeline
from ingestor.datapipe.pipelines.wifi_freifunk_pipeline import WifiFreifunkPipeline
from ingestor.datapipe.pipelines.wifi_myspot_empera_pipeline import (
    WifiMySpotEmperaPipeline,
)
from ingestor.datapipe.pipelines.base_pipeline_types import PipelineType
from ingestor.datapipe.pipelines.emergency_point_pipeline import EmergencyPointPipeline
from ingestor.datapipe.pipelines.wga_events_pipeline import WGAEventPipeline
from ingestor.datapipe.pipelines.ttn_gateway_pipeline import TTNGatewayPipeline

import logging

logger = logging.getLogger(__name__)


class PipelineFactory:
    """Factory to register and create pipelines dynamically."""

    _pipelines = {}

    @classmethod
    def register_pipeline(cls, name, pipeline_cls):
        logger.info(f"Pipeline '{name}' registered!")
        cls._pipelines[name] = pipeline_cls

    @classmethod
    def create_pipeline(cls, name, resources, out_dir, logger, run_record=None):
        if name not in cls._pipelines:
            raise ValueError(f"Pipeline '{name}' not registered")
        return cls._pipelines[name](
            resources=resources, out_dir=out_dir, logger=logger, run_record=run_record
        )


# Register available pipelines
PipelineFactory.register_pipeline(PipelineType.OSM.name, OSMPipeline)
PipelineFactory.register_pipeline(PipelineType.KL_EVENTS.name, KLEventsPipeline)
PipelineFactory.register_pipeline(PipelineType.KL_EVENTS_RIS.name, KLRisEventsPipeline)
PipelineFactory.register_pipeline(PipelineType.KL_GEO_WFS.name, WFSPipeline)
PipelineFactory.register_pipeline(PipelineType.WGA_EVENTS.name, WGAEventPipeline)
PipelineFactory.register_pipeline(PipelineType.TTN_GATEWAY.name, TTNGatewayPipeline)
PipelineFactory.register_pipeline(PipelineType.VRN.name, VRNPipeline)
PipelineFactory.register_pipeline(PipelineType.WIKIPEDIA.name, WikipediaPipeline)
PipelineFactory.register_pipeline(PipelineType.EV_STATIONS.name, EVStationPipeline)
PipelineFactory.register_pipeline(PipelineType.WIFI_FREIFUNK.name, WifiFreifunkPipeline)
PipelineFactory.register_pipeline(
    PipelineType.KL_GEO_RESOURCES.name, KLGeoResourcePipeline
)
PipelineFactory.register_pipeline(
    PipelineType.WIFI_LOCAL.name, WifiMySpotEmperaPipeline
)
PipelineFactory.register_pipeline(
    PipelineType.KL_SENSOR_RESOURCES.name, KLSensorsPipeline
)
PipelineFactory.register_pipeline(
    PipelineType.EMERGENCY_POINTS.name, EmergencyPointPipeline
)
