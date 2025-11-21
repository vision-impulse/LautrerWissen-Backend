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
import asyncio
import asyncpg
import json
import threading
import os
import logging

from ingestor.apis.mqtt.mqtt_stream_consumer import MQTTConsumer
from ingestor.config.env_config import DB_DSN
from ingestor.config.env_config import DB_TABLENAME


logger = logging.getLogger(__name__)

class SensorDBHandler:
    def __init__(self, dsn, flush_interval=5, max_buffer_size=10):
        self.dsn = dsn
        self.flush_interval = flush_interval
        self.max_buffer_size = max_buffer_size
        self.buffer = []
        self.lock = asyncio.Lock()

    async def handle_message(self, message: str):
        try:
            data = json.loads(message)
            if "latitude" in data and "longitude" in data:
                row = (
                    int(data["time"]),
                    float(data["latitude"]),
                    float(data["longitude"]),
                    int(data["sats"]),
                    int(data["battery"]),
                    str(data["triggered"]),
                    int(data["rssi"]),
                    float(data["snr"]),
                    int(data["uplink"]),
                    int(data["downlink"])
                )
                async with self.lock:
                    self.buffer.append(row)
                    if len(self.buffer) >= self.max_buffer_size:
                        await self._flush()
        except Exception as e:
            logger.error("[SensorDBHandler] Parse Error: %s", e, exc_info=True)

    async def _flush(self):
        if len(self.buffer) == 0:
            return
        if not self.buffer:
            return
        try:
            conn = await asyncpg.connect(dsn=self.dsn)
            query = f"""
                INSERT INTO {DB_TABLENAME} (
                    time, latitude, longitude, sats, battery, triggered, rssi, snr, uplink, downlink, created_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW()
                )
            """
            await conn.executemany(query, self.buffer)
            await conn.close()
            logger.info("[SensorDBHandler] Flushed: %s rows to DB.", len(self.buffer))
            self.buffer.clear()
        except Exception as e:
            logger.error("[SensorDBHandler] DB Insert Error: %s", e, exc_info=True)

    async def background_flusher(self):
        while True:
            await asyncio.sleep(self.flush_interval)
            async with self.lock:
                await self._flush()



class MQTTFieldtesterConsumer(MQTTConsumer):

    IDLE_TIMEOUT = 1

    def __init__(self):
        super(MQTTFieldtesterConsumer, self).__init__()
        self.db_handler = SensorDBHandler(DB_DSN)
        # Start the background flusher in a separate thread
        self.loop = asyncio.get_event_loop()
        threading.Thread(target=self.start_background_loop, daemon=True).start()

    def start_background_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.db_handler.background_flusher())

    def on_topic_message_received(self, client, userdata, message, topic):
        try:
            raw = message.payload.decode()
            logger.info("[MQTT] Writing to PostgreSQL from topic: %s", topic)
            asyncio.run_coroutine_threadsafe(self.db_handler.handle_message(raw), self.loop)
        except ValueError as value_error: # JSONDecodeError
            logger.warning("Decoding Error for message %s", value_error, exc_info=True)
        except Exception as e:
            logger.error("Error: %s", e, exc_info=True)
    

