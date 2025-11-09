from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
db_client = None
db = None

async def connect_to_mongo():
    global db_client, db
    
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    cluster = os.getenv("MONGO_CLUSTER")
    app_name = os.getenv("MONGO_APP_NAME")
    db_name = os.getenv("DB_NAME", "interview_video_generator")
    
    # MongoDB connection string
    connection_string = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName={app_name}"
    
    try:
        db_client = AsyncIOMotorClient(connection_string, server_api=ServerApi('1'))
        db = db_client[db_name]
        
        # Test connection
        await db_client.admin.command('ping')
        print(f"✅ Successfully connected to MongoDB database: {db_name}")
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    global db_client
    if db_client:
        db_client.close()
        print("MongoDB connection closed")

def get_database():
    return db

# Collections
def get_ideas_collection():
    return db.ideas

def get_scripts_collection():
    return db.scripts

def get_videos_collection():
    return db.videos

def get_config_collection():
    return db.config

def get_queue_collection():
    """Collection pour la queue de jobs vidéo"""
    return db.video_queue
