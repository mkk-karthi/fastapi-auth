from datetime import timedelta
from typing import Any
from fastapi import Depends, Request
import redis.asyncio as redis

from app.core.config import settings


class RedisCache:
    def __init__(self):
        # constructor must be sync
        self.client: redis.Redis | None = None

    async def connect(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )

        await self.client.ping()

    async def close(self):
        if self.client:
            await self.client.aclose()

    async def set(self, key: str, value: Any, ttl: int):
        await self.client.setex(key, timedelta(minutes=ttl), value)

    async def get(self, key: str):
        return await self.client.get(key)

    async def delete(self, key: str):
        await self.client.delete(key)

def get_redis(request: Request) -> RedisCache:
    return request.app.state.redis


RedisCacheDep = Depends(get_redis)