from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI
            )

            self.db = self.client[
                settings.DATABASE_NAME
            ]

            print("✅ MongoDB connected")

        except Exception as e:
            print(f"Mongo connection failed: {e}")
            raise e

    async def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")


mongodb = MongoDB()