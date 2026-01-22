
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

async def check_users():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    users = await db.users.find({}).to_list(100)
    print(f"Found {len(users)} users.")
    for user in users:
        print(f"User: {user.get('email')}")
        print(f"Password (len={len(user.get('password', ''))}): {user.get('password')}")
        print("-" * 20)
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users())
