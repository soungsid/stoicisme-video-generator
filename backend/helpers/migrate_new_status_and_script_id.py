"""
Script de migration pour ajouter les nouveaux statuts et le champ script_id
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_ideas_collection, get_scripts_collection

async def migrate_database():
    """Migrer la base de données pour ajouter les nouveaux champs"""
    
    # Migration des idées
    ideas_collection = get_ideas_collection()
    scripts_collection = get_scripts_collection()
    
    print("✅ Using existing database connection")
    
    print("🔄 Starting migration...")
    
    # 1. Ajouter script_id aux idées qui ont un script
    print("📝 Adding script_id to ideas...")
    
    # Récupérer tous les scripts
    scripts_cursor = scripts_collection.find({})
    scripts_by_idea = {}
    
    async for script in scripts_cursor:
        idea_id = script.get("idea_id")
        if idea_id:
            scripts_by_idea[idea_id] = script["id"]
    
    # Mettre à jour les idées avec script_id
    updated_count = 0
    for idea_id, script_id in scripts_by_idea.items():
        result = await ideas_collection.update_one(
            {"id": idea_id},
            {"$set": {"script_id": script_id}}
        )
        if result.modified_count > 0:
            updated_count += 1
    
    print(f"✅ Added script_id to {updated_count} ideas")
    
    # 2. Vérifier que tous les statuts existants sont valides
    print("🔍 Checking existing statuses...")
    
    # Les statuts valides selon le nouveau modèle
    valid_statuses = [
        "pending", "queued", "script_generating", "script_generated",
        "audio_generating", "audio_generated", "video_generating", 
        "video_generated", "error"
    ]
    
    # Compter les idées par statut
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    
    status_counts = await ideas_collection.aggregate(pipeline).to_list(length=100)
    
    print("📊 Current status distribution:")
    for stat in status_counts:
        status = stat["_id"]
        count = stat["count"]
        if status in valid_statuses:
            print(f"  ✅ {status}: {count}")
        else:
            print(f"  ⚠️  {status}: {count} (invalid status)")
    
    # 3. Vérifier les idées qui ont un script mais pas le statut script_generated
    print("🔍 Checking ideas with scripts but wrong status...")
    
    ideas_with_script_wrong_status = await ideas_collection.count_documents({
        "script_id": {"$exists": True, "$ne": None},
        "status": {"$nin": ["script_generated", "audio_generated", "audio_generating", "video_generated", "video_generating"]}
    })
    
    if ideas_with_script_wrong_status > 0:
        print(f"⚠️  Found {ideas_with_script_wrong_status} ideas with script but wrong status")
        # Optionnel: corriger automatiquement les statuts
        # await ideas_collection.update_many(
        #     {
        #         "script_id": {"$exists": True, "$ne": None},
        #         "status": {"$nin": ["script_generated", "audio_generated", "audio_generating", "video_generated", "video_generating"]}
        #     },
        #     {"$set": {"status": "script_generated"}}
        # )
        # print(f"✅ Fixed status for {ideas_with_script_wrong_status} ideas")
    
    print("🎉 Migration completed successfully!")
    
    # Statistiques finales
    total_ideas = await ideas_collection.count_documents({})
    ideas_with_script = await ideas_collection.count_documents({"script_id": {"$exists": True, "$ne": None}})
    
    print(f"\n📈 Final statistics:")
    print(f"   Total ideas: {total_ideas}")
    print(f"   Ideas with script_id: {ideas_with_script}")
    print(f"   Ideas without script_id: {total_ideas - ideas_with_script}")

if __name__ == "__main__":
    asyncio.run(migrate_database())
