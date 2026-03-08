from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")
class MongoDB:
    client:AsyncIOMotorClient= None
db= MongoDB()
async def connect_to_mongo():
    #connect mongodb
    db.client= AsyncIOMotorClient(MONGODB_URL)
    print(f"Connected to MongDB: {DB_NAME}")
async def close_mongo_connection():
    db.client.close()
    print("MongoDB connect closed")
def get_databse():
    return db.client[DB_NAME]


#collection of mongodb
def get_users_collection():
    return get_databse()["users"]
def get_predictions_collection():
    return get_databse()["predictions"]
def get_doctors_collection():
    return get_databse()["doctors"]


