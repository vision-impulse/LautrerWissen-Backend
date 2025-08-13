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

import argparse
import logging

from ingestor.apis.mqtt.mqtt_stream_fieldtester import MQTTFieldtesterConsumer
from ingestor.apis.mqtt.mqtt_stream_sensors_redis import MQTTSensorConsumer
from ingestor.utils.logging_utils import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Run a mqtt streaming consumer.")
    parser.add_argument(
        "--sensor",
        choices=["fieldtester", "sensors"],
        required=True,
        help="Specify which mqtt consumer to run",
    )
    args = parser.parse_args()

    if args.sensor == "fieldtester":
        setup_logging(log_file="mqtt-streaming-fieldtester.log", level=logging.INFO)
        MQTTFieldtesterConsumer().run()
    elif args.sensor == "sensors":
        setup_logging(log_file="mqtt-streaming-sensors.log", level=logging.INFO)
        MQTTSensorConsumer().run()


if __name__ == "__main__":
    main()
