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

import time
import os
import re
import logging
import threading

from typing import Optional
from paho.mqtt import client as mqtt_client
from abc import ABC, abstractmethod
from ingestor.config.env_config import MQTT_BROKER
from ingestor.config.env_config import MQTT_PORT
from ingestor.config.env_config import MQTT_USERNAME
from ingestor.config.env_config import MQTT_PASSWORD
from ingestor.config.env_config import MQTT_HEARTBEAT_INTERVAL
from ingestor.config.env_config import MQTT_HEARTBEAT_FILE_PATH
from ingestor.config.env_config import MQTT_TOPIC_SELECTOR


logger = logging.getLogger(__name__)


def write_heartbeat_file(file_path: str = MQTT_HEARTBEAT_FILE_PATH):
    """
    Writes the current Unix timestamp to a file which acts as a 'heartbeat' for external monitoring.
    """
    try:
        # Overwrite the file with the new timestamp
        with open(file_path, 'w') as f:
            f.write(str(time.time()))
        return None
    except Exception as e:
        logger.error("ERROR: Could not securely write heartbeat file %s: %s", file_path, e)
        return e


class MQTTConsumer(ABC):
    
    IDLE_TIMEOUT = 1

    def __init__(self):
        super(MQTTConsumer, self).__init__()
        self.broker = MQTT_BROKER
        self.port = int(MQTT_PORT)
        self.username = MQTT_USERNAME
        self.pasw = MQTT_PASSWORD
        self.start_time = time.time()
        self.client = mqtt_client.Client()
        self.compiled_patterns = [re.compile(p.strip()) for p in MQTT_TOPIC_SELECTOR.split(",") if p.strip()]

    @abstractmethod
    def on_topic_message_received(self, client, userdata, message, topic):
        pass

    def run(self):
        self._start_heartbeat_writer()
        self.client.tls_set()
        self.client.enable_logger()
        self.client.username_pw_set(self.username, self.pasw)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()

    def _start_heartbeat_writer(self):
        def heartbeat_loop():
            while True:
                write_heartbeat_file()
                time.sleep(MQTT_HEARTBEAT_INTERVAL)
        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

    def _matches_topics(self, topic: str) -> bool:
        return any(p.search(topic) for p in self.compiled_patterns)

    def _on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            logger.error("Failed to connect to MQTT Broker! %s", MQTT_BROKER)
            logger.error(rc)
            exit(0)
        logger.info("Connected to MQTT Broker! %s", MQTT_BROKER)
        client.subscribe("#")

    def _on_message(self, client, userdata, message):
        try:
            topic = message.topic
            if self._matches_topics(topic):
                self.on_topic_message_received(client, userdata, message, topic)
        except Exception as e:
            logger.error("Parse Error: %s", e, exc_info=True)
    
