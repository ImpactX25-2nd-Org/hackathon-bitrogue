"""
Database module for MongoDB connection using Motor (async driver)
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from typing import Optional


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB on application startup"""
    print(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URI)
    db.db = db.client[settings.DATABASE_NAME]
    
    # Test connection
    try:
        await db.client.admin.command('ping')
        print(f"✓ Successfully connected to MongoDB database: {settings.DATABASE_NAME}")
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection on application shutdown"""
    if db.client:
        print("Closing MongoDB connection...")
        db.client.close()
        print("✓ MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance for dependency injection"""
    return db.db


# Collection names (for reference)
COLLECTIONS = {
    "users": "users",
    "scans": "scans",
    "community_posts": "community_posts",
    "post_comments": "post_comments",
    "suggestions": "suggestions",
    "notifications": "notifications",
    "follow_ups": "follow_ups",
}
