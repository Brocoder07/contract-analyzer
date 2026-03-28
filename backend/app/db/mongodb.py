from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.core.config import settings

_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return _client


def get_database() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("MongoDB database is not initialized")
    return _database


def get_users_collection() -> AsyncIOMotorCollection:
    return get_database()[settings.MONGODB_USERS_COLLECTION]


async def connect_to_mongo() -> None:
    global _client, _database
    if _client is not None:
        return

    _client = AsyncIOMotorClient(settings.MONGODB_URI)
    _database = _client[settings.MONGODB_DB_NAME]

    # Ensure critical index(es)
    users = get_users_collection()
    await users.create_index("email", unique=True)


async def close_mongo_connection() -> None:
    global _client, _database
    if _client is not None:
        _client.close()
    _client = None
    _database = None
