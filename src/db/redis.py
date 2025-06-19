import redis.asyncio as redis
from src.config import Config

JTI_EXPIRED = 3600

redis_client = redis.from_url(Config.REDIS_URL)


async def add_jti_to_blocklist(jti: str) -> None:
    await redis_client.set(name=jti, value="", ex=JTI_EXPIRED)


async def token_in_blocklist(jti: str) -> bool:
    result = await redis_client.get(jti)
    return result is not None


async def remove_from_blocklist(jti: str) -> None:
    await redis_client.delete(jti)


async def close_redis_connection():
    await redis_client.close()
