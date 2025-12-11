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

import os
import urllib.parse

SENSOR_TYPE_CONFIG_PATH = "/config/init/sensor_types.yaml"

WASGEHTAPP_USER = os.getenv('WASGEHTAPP_USER')
WASGEHTAPP_PASS = os.getenv('WASGEHTAPP_PASS')

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = os.getenv("MQTT_PORT")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC_SELECTOR = os.getenv("MQTT_TOPIC_SELECTOR", "*")
MQTT_HEARTBEAT_FILE_PATH = os.getenv("MQTT_HEARTBEAT_FILE_PATH", "/logs/heartbeat.log") 
MQTT_HEARTBEAT_INTERVAL = int(os.getenv("MQTT_HEARTBEAT_INTERVAL", 60*10))

DB_NAME = os.getenv('DATABASE_NAME')
DB_USER = os.getenv('DATABASE_USER')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD')
DB_HOST = os.getenv('DATABASE_HOST')
DB_PORT = os.getenv('DATABASE_PORT')
DB_DSN = (
    f"postgresql://{DB_USER}:{urllib.parse.quote(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
DB_TABLENAME = "lautrer_wissen_klfieldtestmeasurements"

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379) 




