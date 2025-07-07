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
import redis
import json
import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import redis.asyncio as aioredis  


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.redis = aioredis.Redis(host='redis', port=6379, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.topic = None
        self.reader_task = None

    async def disconnect(self, close_code):
        if self.reader_task:
            self.reader_task.cancel()
        if self.pubsub and self.topic:
            await self.pubsub.unsubscribe(self.topic)
            await self.pubsub.close()
        await self.redis.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        self.topic = data.get("topic")
        if not self.topic:
            await self.send(json.dumps({"error": "No topic provided"}))
            return

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

        async def reader():
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    print(message)
                    try:
                        payload = json.loads(message['data'])                    
                    except json.JSONDecodeError:
                        payload = ""
                    await self.send(json.dumps({
                        "topic": self.topic,
                        "sensor_data":  payload 
                    }))

        # Start reader in background
        self.reader_task = asyncio.create_task(reader())
