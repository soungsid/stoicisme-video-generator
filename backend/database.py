from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os

# MongoDB connection
db_client = None
db = None

async def connect_to_mongo():
    global db_client, db
    
    username = os.getenv("MONGO_USERNAME", "soungsid")
    password = os.getenv("MONGO_PASSWORD", "MFBfO3IKdE4RqbRd")
    cluster = os.getenv("MONGO_CLUSTER", "cluster0.tmklvts.mongodb.net")
    app_name = os.getenv("MONGO_APP_NAME", "Cluster0")
    db_name = os.getenv("DB_NAME", "stoicisme_video_generator_staging")
    
    print(f"📊 Connecting to MongoDB with:")
    print(f"  - Username: {username}")
    print(f"  - Cluster: {cluster}")
    print(f"  - DB Name: {db_name}")
    
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
    return get_database().ideas

def get_scripts_collection():
    return get_database().scripts

def get_videos_collection():
    return get_database().videos

def get_config_collection():
    return get_database().config

def get_queue_collection():
    """Collection pour la queue de jobs vidéo"""
    return get_database().video_queue
