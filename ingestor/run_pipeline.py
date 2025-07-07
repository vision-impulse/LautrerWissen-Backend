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

from ingestor.datapipe.config import load_config
from ingestor.datapipe.manager import PipelineManager
from ingestor.datapipe.pipelines.base_pipeline import PipelineType
from ingestor.utils.logging_utils import get_logger

import argparse
import os 


def parse_arguments():
    """
    Parses command-line arguments for -source.

    -source (-s): The data source ('wiki', 'osm', 'city', 'vrn').

    Returns:
        args (Namespace): Parsed arguments.
    """
    # Initialize the argument parser
    parser = argparse.ArgumentParser(
        description="Script to run data pipelines (download, transform, import) for external data sources."
    )
    # Add arguments
    parser.add_argument(
        "-source", "-s",
        choices=["wiki", "osm", "wfs", "miadi", "ris", "vrn", "emergency", "wifilocal", "freifunk",
                 "georesouces", "sensors", "ev", "ttn", "wga", "all",  ],
        required=False,
        help="Specify the data source."
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()
    print(f"Running pipeline for source: {args.source}")
    logger = get_logger()
    config_file = os.path.join(os.getenv("APP_DATA_DIR"), "/initial/config/config.yaml")
    config = load_config(config_file)
    outdir = config.out_dir
    
    manager = PipelineManager(logger)

    if args.source == "all":
        manager.run_pipeline(PipelineType.EMERGENCY_POINTS, config.get_resources(PipelineType.EMERGENCY_POINTS), outdir)
        manager.run_pipeline(PipelineType.VRN, config.get_resources(PipelineType.VRN), outdir)
        manager.run_pipeline(PipelineType.KL_EVENTS, config.get_resources(PipelineType.KL_EVENTS), outdir)
        manager.run_pipeline(PipelineType.KL_EVENTS_RIS, config.get_resources(PipelineType.KL_EVENTS_RIS), outdir)
        manager.run_pipeline(PipelineType.WGA_EVENTS, config.get_resources(PipelineType.WGA_EVENTS), outdir)
        manager.run_pipeline(PipelineType.OSM, config.get_resources(PipelineType.OSM), outdir)
        manager.run_pipeline(PipelineType.KL_GEO_WFS, config.get_resources(PipelineType.KL_GEO_WFS), outdir)
        manager.run_pipeline(PipelineType.WIFI_LOCAL, config.get_resources(PipelineType.WIFI_LOCAL), outdir)
        manager.run_pipeline(PipelineType.WIFI_FREIFUNK, config.get_resources(PipelineType.WIFI_FREIFUNK), outdir)
        manager.run_pipeline(PipelineType.KL_GEO_RESOURCES, config.get_resources(PipelineType.KL_GEO_RESOURCES), outdir)
        manager.run_pipeline(PipelineType.KL_SENSOR_RESOURCES, config.get_resources(PipelineType.KL_SENSOR_RESOURCES), outdir)
        manager.run_pipeline(PipelineType.WIKIPEDIA, config.get_resources(PipelineType.WIKIPEDIA), outdir)

    if args.source == "emergency":
        manager.run_pipeline(PipelineType.EMERGENCY_POINTS, config.get_resources(PipelineType.EMERGENCY_POINTS), outdir)
    elif args.source == "vrn":
        manager.run_pipeline(PipelineType.VRN, config.get_resources(PipelineType.VRN), outdir)
    elif args.source == "miadi":
        manager.run_pipeline(PipelineType.KL_EVENTS, config.get_resources(PipelineType.KL_EVENTS), outdir)
    elif args.source == "ris":
        manager.run_pipeline(PipelineType.KL_EVENTS_RIS, config.get_resources(PipelineType.KL_EVENTS_RIS), outdir)
    elif args.source == "wga":
        manager.run_pipeline(PipelineType.WGA_EVENTS, config.get_resources(PipelineType.WGA_EVENTS), outdir)
    elif args.source == "osm":
        manager.run_pipeline(PipelineType.OSM, config.get_resources(PipelineType.OSM), outdir)
    elif args.source == "wfs":
        manager.run_pipeline(PipelineType.KL_GEO_WFS, config.get_resources(PipelineType.KL_GEO_WFS), outdir)
    elif args.source == "wifilocal":
        manager.run_pipeline(PipelineType.WIFI_LOCAL, config.get_resources(PipelineType.WIFI_LOCAL), outdir)
    elif args.source == "freifunk":
        manager.run_pipeline(PipelineType.WIFI_FREIFUNK, config.get_resources(PipelineType.WIFI_FREIFUNK), outdir)
    elif args.source == "georesouces":
        manager.run_pipeline(PipelineType.KL_GEO_RESOURCES, config.get_resources(PipelineType.KL_GEO_RESOURCES), outdir)
    elif args.source == "sensors":
        manager.run_pipeline(PipelineType.KL_SENSOR_RESOURCES, config.get_resources(PipelineType.KL_SENSOR_RESOURCES), outdir)
    elif args.source == "wiki":
        manager.run_pipeline(PipelineType.WIKIPEDIA, config.get_resources(PipelineType.WIKIPEDIA), outdir)
    elif args.source == "ev":
        manager.run_pipeline(PipelineType.EV_STATIONS, config.get_resources(PipelineType.EV_STATIONS), outdir)
    elif args.source == "ttn":
        manager.run_pipeline(PipelineType.TTN_GATEWAY, config.get_resources(PipelineType.TTN_GATEWAY), outdir)


