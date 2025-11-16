from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import asyncio
import sys
import os

# Ajouter le répertoire parent au chemin Python pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_ideas_collection, get_scripts_collection, get_videos_collection
from helpers.migrate_db import migrate_idea_statuses
from helpers.migrate_new_status_and_script_id import migrate_database

router = APIRouter()

@router.post("/run", response_model=Dict[str, Any])
async def run_migrations():
    """
    Exécuter toutes les migrations disponibles et retourner les statistiques
    """
    try:
        results = {
            "success": True,
            "migrations": [],
            "statistics": {}
        }
        
        # Migration 1: Statuts des idées
        print("🔄 Running migration: migrate_idea_statuses")
        try:
            await migrate_idea_statuses()
            results["migrations"].append({
                "name": "migrate_idea_statuses",
                "status": "completed",
                "description": "Migration des anciens statuts vers le nouveau système"
            })
        except Exception as e:
            results["migrations"].append({
                "name": "migrate_idea_statuses",
                "status": "failed",
                "error": str(e),
                "description": "Migration des anciens statuts vers le nouveau système"
            })
        
        # Migration 2: Nouveaux statuts et script_id
        print("🔄 Running migration: migrate_new_status_and_script_id")
        try:
            await migrate_database()
            results["migrations"].append({
                "name": "migrate_new_status_and_script_id",
                "status": "completed",
                "description": "Ajout des nouveaux statuts et du champ script_id"
            })
        except Exception as e:
            results["migrations"].append({
                "name": "migrate_new_status_and_script_id",
                "status": "failed",
                "error": str(e),
                "description": "Ajout des nouveaux statuts et du champ script_id"
            })
        
        # Récupérer les statistiques après migration
        results["statistics"] = await get_database_statistics()
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running migrations: {str(e)}"
        )

@router.get("/statistics", response_model=Dict[str, Any])
async def get_migration_statistics():
    """
    Récupérer les statistiques de la base de données
    """
    try:
        statistics = await get_database_statistics()
        return {
            "success": True,
            "statistics": statistics
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}"
        )

async def get_database_statistics() -> Dict[str, Any]:
    """
    Récupérer les statistiques détaillées de la base de données
    """
    try:
        ideas_collection = get_ideas_collection()
        scripts_collection = get_scripts_collection()
        videos_collection = get_videos_collection()
        
        # Statistiques des idées
        total_ideas = await ideas_collection.count_documents({})
        ideas_with_script = await ideas_collection.count_documents({"script_id": {"$exists": True, "$ne": None}})
        
        # Distribution des statuts des idées
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_counts = await ideas_collection.aggregate(status_pipeline).to_list(length=100)
        status_distribution = {stat["_id"]: stat["count"] for stat in status_counts}
        
        # Statistiques des scripts
        total_scripts = await scripts_collection.count_documents({})
        
        # Scripts par statut
        script_status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        script_status_counts = await scripts_collection.aggregate(script_status_pipeline).to_list(length=100)
        script_status_distribution = {stat["_id"]: stat["count"] for stat in script_status_counts}
        
        # Statistiques des vidéos
        total_videos = await videos_collection.count_documents({})
        
        # Vidéos par statut
        video_status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        video_status_counts = await videos_collection.aggregate(video_status_pipeline).to_list(length=100)
        video_status_distribution = {stat["_id"]: stat["count"] for stat in video_status_counts}
        
        # Calcul des pourcentages
        script_coverage = (ideas_with_script / total_ideas * 100) if total_ideas > 0 else 0
        
        return {
            "ideas": {
                "total": total_ideas,
                "with_script": ideas_with_script,
                "without_script": total_ideas - ideas_with_script,
                "script_coverage_percentage": round(script_coverage, 2),
                "status_distribution": status_distribution
            },
            "scripts": {
                "total": total_scripts,
                "status_distribution": script_status_distribution
            },
            "videos": {
                "total": total_videos,
                "status_distribution": video_status_distribution
            },
            "summary": {
                "total_items": total_ideas + total_scripts + total_videos,
                "completion_rate": round(script_coverage, 2)
            }
        }
        
    except Exception as e:
        print(f"Error getting database statistics: {e}")
        return {
            "ideas": {"total": 0, "with_script": 0, "without_script": 0, "script_coverage_percentage": 0, "status_distribution": {}},
            "scripts": {"total": 0, "status_distribution": {}},
            "videos": {"total": 0, "status_distribution": {}},
            "summary": {"total_items": 0, "completion_rate": 0}
        }
