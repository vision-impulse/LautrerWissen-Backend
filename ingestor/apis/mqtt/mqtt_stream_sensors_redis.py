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
import redis
from zoneinfo import ZoneInfo


MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = os.getenv("MQTT_PORT")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_HOSTNAME = "redis"
REDIS_PORT = 6379


class MQTTSensorConsumer():

    IDLE_TIMEOUT = 1

    def __init__(self):
        super(MQTTSensorConsumer, self).__init__()
        self.broker = MQTT_BROKER
        self.port = int(MQTT_PORT)
        self.username = MQTT_USERNAME
        self.pasw = MQTT_PASSWORD
        self.start_time = time.time()
        self.client = mqtt_client.Client()
        self.redis_cache = redis.Redis(host=REDIS_HOSTNAME, port=REDIS_PORT, decode_responses=True)
        
    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print("Failed to connect to MQTT Broker!", MQTT_BROKER)
            print(rc)
            exit(0)
        print("Connected to MQTT Broker!", MQTT_BROKER)
        client.subscribe("#")

    def on_message(self, client, userdata, message):
        topic = message.topic
        if topic.startswith("geo") and "sensor" in topic:
            raw = message.payload.decode()
            data = json.loads(raw)
            if "latitude" in data and "longitude" in data:
                print("Writing to redis_cache on ", topic), 
                try:
                    dt = datetime.fromtimestamp(int(data["time"]) / 1000, tz=ZoneInfo("Europe/Berlin"))
                    data["time"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print("Error converting timestamp", e)
                    pass
                print(data)
                updated_data = json.dumps(data)
                self.redis_cache.hset('sensor_data', topic, updated_data)
                self.redis_cache.publish(topic, updated_data) 
                
    def run(self):
        self.client.tls_set()
        self.client.enable_logger()
        self.client.username_pw_set(self.username, self.pasw)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()

