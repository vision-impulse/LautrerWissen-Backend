# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Vision Impulse GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
AGPL License: https://www.gnu.org/licenses/agpl-3.0.en.html

Authors:
    - benjamin.bischke@vision-impulse.com
"""

import json
import asyncio
import redis.asyncio as redis

from channels.generic.websocket import AsyncWebsocketConsumer
from webapp.settings import REDIS_URL

_redis_client = None

def get_redis():
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
            max_connections=10 
        )
    return _redis_client


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.redis = get_redis()
        self.pubsub = self.redis.pubsub()
        self.topic = None
        self.reader_task = None

    async def disconnect(self, close_code):
        if self.reader_task:
            self.reader_task.cancel()
            try:
                await self.reader_task
            except asyncio.CancelledError:
                pass
        if self.pubsub:
            await self.pubsub.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        topic = data.get("topic")

        if not topic:
            await self.send(json.dumps({"error": "No topic provided"}))
            return

        # Cancel old reader if switching topics
        if self.reader_task:
            self.reader_task.cancel()
            try:
                await self.reader_task
            except asyncio.CancelledError:
                pass

        if self.topic:
            await self.pubsub.unsubscribe(self.topic)

        self.topic = topic

        # Send current value from Redis
        latest = await self.redis.hget("sensor_data", self.topic)
        if latest:
            try:
                payload = json.loads(latest)
            except json.JSONDecodeError:
                payload = latest
            await self.send(json.dumps({"topic": self.topic, "sensor_data": payload}))
        # Subscribe to topic
        await self.pubsub.subscribe(self.topic)

        async def reader(local_topic):
            try:
                async for message in self.pubsub.listen():
                    if message["type"] == "message":
                        try:
                            payload = json.loads(message["data"])
                        except json.JSONDecodeError:
                            payload = ""

                        await self.send(json.dumps({
                            "topic": local_topic,
                            "sensor_data": payload
                        }))
            except asyncio.CancelledError:
                pass
        
        # Start reader in background
        self.reader_task = asyncio.create_task(reader(topic))
