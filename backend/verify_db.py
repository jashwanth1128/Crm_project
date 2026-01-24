from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

async def check_connection():
    mongo_url = os.environ.get('MONGO_URL')
    print(f"Testing connection to: {mongo_url.split('@')[1] if '@' in mongo_url else 'Invalid URL structure'}")
    
    try:
        client = AsyncIOMotorClient(mongo_url)
        # The is_master command is cheap and does not require auth.
        await client.admin.command('ismaster')
        print("Connected to MongoDB successfully!")
        
        db = client[os.environ.get('DB_NAME')]
        print(f"Using database: {db.name}")
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_connection())
