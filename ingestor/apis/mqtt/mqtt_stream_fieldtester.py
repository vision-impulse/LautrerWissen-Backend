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
import json
import asyncio
import asyncpg
import json
import threading
import time
import os


MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = os.getenv("MQTT_PORT")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

DB_NAME = os.getenv('DATABASE_NAME')
DB_USER = os.getenv('DATABASE_USER')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD')
DB_HOST = os.getenv('DATABASE_HOST')
DB_PORT = os.getenv('DATABASE_PORT')

DB_DSN = "postgresql://%s:%s@%s:%s/%s" %(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
TABLENAME = "lautrer_wissen_klfieldtestmeasurements"


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
            print(f"[Handler] Parse Error: {e}")

    async def _flush(self):
        if len(self.buffer) == 0:
            return
        if not self.buffer:
            return
        try:
            conn = await asyncpg.connect(dsn=self.dsn)
            query = f"""
                INSERT INTO {TABLENAME} (
                    time, latitude, longitude, sats, battery, triggered, rssi, snr, uplink, downlink, created_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW()
                )
            """
            await conn.executemany(query, self.buffer)
            await conn.close()
            print(f"[Handler] Flushed {len(self.buffer)} rows to DB.")
            self.buffer.clear()
        except Exception as e:
            print(f"[Handler] DB Insert Error: {e}")

    async def background_flusher(self):
        while True:
            await asyncio.sleep(self.flush_interval)
            async with self.lock:
                await self._flush()



class MQTTFieldtesterConsumer():

    IDLE_TIMEOUT = 1

    def __init__(self):
        super(MQTTFieldtesterConsumer, self).__init__()
        self.broker = MQTT_BROKER
        self.port = int(MQTT_PORT)
        self.username = MQTT_USERNAME
        self.pasw = MQTT_PASSWORD
        self.start_time = time.time()
        self.client = mqtt_client.Client()

        self.db_handler = SensorDBHandler(DB_DSN)
        
        # Start the background flusher in a separate thread
        self.loop = asyncio.get_event_loop()
        threading.Thread(target=self.start_background_loop, daemon=True).start()

    def start_background_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.db_handler.background_flusher())

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print("Failed to connect to MQTT Broker!", self.broker)
            return
        print("Connected to MQTT Broker!", self.broker)
        client.subscribe("#")

    def on_message(self, client, userdata, message):
        topic = message.topic
        if "fieldtester" in topic:
            raw = message.payload.decode()
            print(f"[MQTT] Writing to PostgreSQL from topic: {topic}")
            asyncio.run_coroutine_threadsafe(self.db_handler.handle_message(raw), self.loop)

    def run(self):
        self.client.tls_set()
        self.client.enable_logger()
        self.client.username_pw_set(self.username, self.pasw)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()


