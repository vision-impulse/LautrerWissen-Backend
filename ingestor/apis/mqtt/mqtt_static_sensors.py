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


from paho.mqtt import client as mqtt_client
from datetime import datetime
import random
import json
import time
import yaml
import os
import logging

from ingestor.apis import Downloader

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = os.getenv("MQTT_PORT")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")


class MQTTInitialSensorsDownloader(Downloader):

    IDLE_TIMEOUT = 1

    def __init__(self, out_dir, mqtt_resource, logger):
        super(MQTTInitialSensorsDownloader, self).__init__(out_dir)
        self.broker = MQTT_BROKER
        self.port = int(MQTT_PORT)
        self.username = MQTT_USERNAME
        self.pasw = MQTT_PASSWORD
        self.logger = logger
        self.start_time = time.time()
        self.client = mqtt_client.Client()
        self.available_sensors = {}
        self.out_dir = out_dir
        self.out_fp = os.path.join(self.out_dir, mqtt_resource.filename)
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.start_time = time.time()
            self.logger.info("Connected to MQTT Broker! %s", MQTT_BROKER)
            client.subscribe("#")
        else:
            self.logger.error("Failed to connect to MQTT Broker! %s", MQTT_BROKER)
            self.logger.error(rc)

    def write_to_yaml(self):
        yaml_data = {
            "sensors": [ data for _topic, data in self.available_sensors.items()]
        }
        with open(self.out_fp, "w") as f:
            yaml.dump(yaml_data, f, sort_keys=False)

    def sensor_has_valid_gps_position(self, sensor_data):
        return ("latitude" in sensor_data and sensor_data["latitude"] is not None and \
                "longitude" in sensor_data and sensor_data["longitude"] is not None)

    def on_message(self, client, userdata, message):
        elapsed = time.time() - self.start_time
        if elapsed >= MQTTInitialSensorsDownloader.IDLE_TIMEOUT:
            self.client.disconnect()
        topic = message.topic
        try:
            raw = message.payload.decode()
            data = json.loads(raw)
            self.logger.info("Analyzing topic %s", topic)
            if topic.startswith("geo") and "sensor" in topic:
                if self.sensor_has_valid_gps_position(data):
                    self.available_sensors[topic] = {
                        "topic": topic,
                        "sensor_latitude": data["latitude"],
                        "sensor_longitude": data["longitude"],
                    }
        except Exception as e:
            self.logger.error("Parse Error: %s", e, exc_info=True)

    def perform_download(self):
        self.client.tls_set()
        self.client.enable_logger()
        self.client.username_pw_set(self.username, self.pasw)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()
        self.write_to_yaml()
