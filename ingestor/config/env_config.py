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

def load_secrets(file_path):
    secrets = {}
    if not os.path.exists(file_path):
        return secrets

    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                secrets[key] = value
    return secrets


SENSOR_TYPE_CONFIG_PATH = "/config/init/sensor_types.yaml"

# -----------------------------------------------------------------------------
#       Redis
# -----------------------------------------------------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379) 

# -----------------------------------------------------------------------------
#       WGA
# -----------------------------------------------------------------------------
wga_secrets = load_secrets("/run/secrets/wga_secrets")
WASGEHTAPP_USER = wga_secrets.get('WASGEHTAPP_USERNAME')
WASGEHTAPP_PASS = wga_secrets.get('WASGEHTAPP_PASSWORD')

# -----------------------------------------------------------------------------
#       MQTT
# -----------------------------------------------------------------------------
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = os.getenv("MQTT_PORT")
MQTT_TOPIC_SELECTOR = os.getenv("MQTT_TOPIC_SELECTOR", "*")
MQTT_HEARTBEAT_FILE_PATH = os.getenv("MQTT_HEARTBEAT_FILE_PATH", "/logs/heartbeat.log") 
MQTT_HEARTBEAT_INTERVAL = int(os.getenv("MQTT_HEARTBEAT_INTERVAL", 60*10))

mqtt_secrets = load_secrets("/run/secrets/mqtt_secrets")
MQTT_USERNAME = mqtt_secrets.get("MQTT_USERNAME")
MQTT_PASSWORD = mqtt_secrets.get("MQTT_PASSWORD")

# -----------------------------------------------------------------------------
#       Database
# -----------------------------------------------------------------------------
DB_HOST = os.getenv('DATABASE_HOST')
DB_PORT = os.getenv('DATABASE_PORT')
DB_TABLENAME = "lautrer_wissen_klfieldtestmeasurements"

db_secrets = load_secrets("/run/secrets/db_secrets")
DB_PASSWORD = db_secrets.get("POSTGRES_PASSWORD")
DB_USER = db_secrets.get("POSTGRES_USER")
DB_NAME = db_secrets.get("POSTGRES_DB")