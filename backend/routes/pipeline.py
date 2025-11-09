from fastapi import APIRouter, HTTPException, status
from models import IdeaStatus
from database import get_ideas_collection, get_scripts_collection
from services.queue_service import QueueService
import traceback

router = APIRouter()

@router.post("/generate/{idea_id}")
async def start_pipeline(idea_id: str, start_from: str = "script"):
    """
    Ajouter une génération à la queue
    start_from: 'script', 'adapt', 'audio', 'video'
    """
    try:
        ideas_collection = get_ideas_collection()
        idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
        
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        if idea["status"] == IdeaStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Idea must be validated first"
            )
        
        # Ajouter à la queue au lieu de lancer en background
        queue_service = QueueService()
        job = await queue_service.add_job(idea_id, start_from)
        
        # Obtenir la position dans la queue
        position = await queue_service.get_queue_position(idea_id)
        
        return {
            "success": True,
            "message": "Job added to queue",
            "job_id": job.job_id,
            "idea_id": idea_id,
            "queue_position": position,
            "start_from": start_from
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding to queue: {str(e)}"
        )

@router.get("/status/{idea_id}")
async def get_pipeline_status(idea_id: str):
    """Obtenir le statut du pipeline"""
    try:
        ideas_collection = get_ideas_collection()
        idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
        
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        return {
            "idea_id": idea_id,
            "status": idea["status"],
            "progress_percentage": idea.get("progress_percentage", 0),
            "current_step": idea.get("current_step"),
            "error_message": idea.get("error_message")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting status: {str(e)}"
        )
