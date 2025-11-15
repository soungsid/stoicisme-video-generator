import asyncio
import sys
import os

# Ajouter le répertoire parent au chemin Python pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import connect_to_mongo, close_mongo_connection, get_ideas_collection

async def migrate_idea_statuses():
    """
    Met à jour les anciens statuts des idées vers le nouveau système de statuts simplifié.
    """
    try:
        await connect_to_mongo()
        print("✅ Connected to MongoDB via database.py")
        
        ideas_collection = get_ideas_collection()
        
        status_mapping = {
            "processing": "queued",
            "script_generating": "queued",
            "script_adapting": "script_generated",
            "script_adapted": "script_generated",
            "audio_generating": "script_generated",
            "video_generating": "audio_generated",
            "uploaded": "video_generated",
            "validated": "pending",
            "rejected": "pending"
        }
        
        print("🔍 Starting migration of idea statuses...")
        updated_count = 0
        
        async for idea in ideas_collection.find():
            current_status = idea.get("status")
            if current_status in status_mapping:
                new_status = status_mapping[current_status]
                await ideas_collection.update_one(
                    {"_id": idea["_id"]},
                    {"$set": {"status": new_status}}
                )
                print(f"  - Updated idea {idea['id']}: '{current_status}' -> '{new_status}'")
                updated_count += 1
        
        print(f"✅ Migration complete. {updated_count} ideas updated.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        await close_mongo_connection()
        print("🔌 MongoDB connection closed.")

if __name__ == "__main__":
    asyncio.run(migrate_idea_statuses())
