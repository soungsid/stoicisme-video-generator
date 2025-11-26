"""
Script de migration pour ajouter les nouveaux statuts et le champ script_id
"""
import asyncio
from datetime import datetime
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_ideas_collection, connect_to_mongo

async def clean_generated_image_from_db():
    """Migrer la base de données pour supprimer les infos sur les images generées"""
    await connect_to_mongo()
    # Migration des idées
    ideas_collection = get_ideas_collection()
    print("cleaning images on ")
    
    idea_cursor = ideas_collection.find({})
    async for idea in idea_cursor:
        print(f" ⚙️ updating idea {idea.get("id")}-{idea.get("title")}")

        await ideas_collection.update_one(
            {"id": idea["id"]},
            {
                "$set": {
                    "image_prompts": [],
                    "generated_images": [],
                    "total_images": 0,
                    "images_generated_at": datetime.now().isoformat()
                }
            }
        )
        
    
    # 3. Vérifier les idées qui ont un script mais pas le statut script_generated
    print("✅ Toutes les images ont été mis à jour.")

if __name__ == "__main__":
    asyncio.run(clean_generated_image_from_db())
