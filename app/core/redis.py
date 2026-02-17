from datetime import timedelta
import redis.asyncio as redis

from app.core.config import settings


class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )

    async def set(self, key, value, ttl):
        await self.client.setex(key, timedelta(minutes=ttl), value)

    async def get(self, key):
        return await self.client.get(key)

    async def delete(self, key):
        await self.client.delete(key)


redisCache = RedisCache()

__all__ = ["RedisCache", "redisCache"]
