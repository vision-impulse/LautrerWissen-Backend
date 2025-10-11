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


import json
import os
import redis
import logging

from datetime import datetime
from zoneinfo import ZoneInfo
from ingestor.apis.mqtt.mqtt_stream_consumer import MQTTConsumer

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379) 

logger = logging.getLogger(__name__)


class MQTTSensorConsumer(MQTTConsumer):

    IDLE_TIMEOUT = 1

    def __init__(self):
        super(MQTTSensorConsumer, self).__init__()
        self.redis_cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    def on_topic_message_received(self, client, userdata, message, topic):
        try:
            raw = message.payload.decode()
            data = json.loads(raw)
            if "latitude" in data and "longitude" in data:
                logger.info("Writing to redis_cache on %s", topic)
                try:
                    dt = datetime.fromtimestamp(int(data["time"]) / 1000, 
                                                tz=ZoneInfo("Europe/Berlin"))
                    data["time"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    logger.error("Error converting timestamp %s", e)
                    pass
                logger.info("Writing to redis_cache data %s", data)
                updated_data = json.dumps(data)
                self.redis_cache.hset('sensor_data', topic, updated_data)
                self.redis_cache.publish(topic, updated_data) 
        except ValueError as value_error: # JSONDecodeError
            logger.warning("Decoding Error for message %s", value_error, exc_info=True)
        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
        