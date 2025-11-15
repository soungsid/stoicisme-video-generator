"""
Routes pour la gestion de la queue de jobs
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from models import JobStatus
from services.queue_service import QueueService
from database import get_ideas_collection

router = APIRouter()

@router.get("/stats")
async def get_queue_stats():
    """
    Obtenir les statistiques de la queue
    """
    try:
        queue_service = QueueService()
        stats = await queue_service.get_queue_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting queue stats: {str(e)}"
        )

@router.get("/jobs")
async def get_all_jobs(status: Optional[JobStatus] = None):
    queue_service = QueueService()
    jobs = await queue_service.list_all_jobs(status=status)
    return jobs
    
@router.get("/status/{idea_id}")
async def get_job_status(idea_id: str):
    """
    Obtenir le statut d'un job dans la queue pour une idée donnée
    """
    try:
        queue_service = QueueService()
        
        # Récupérer le job
        job = await queue_service.get_job_by_idea(idea_id)
        
        if not job:
            return {
                "has_job": False,
                "idea_id": idea_id
            }
        
        # Obtenir la position dans la queue si en attente
        position = None
        if job.status == "queued":
            position = await queue_service.get_queue_position(idea_id)
        
        return {
            "has_job": True,
            "job_id": job.job_id,
            "idea_id": idea_id,
            "status": job.status,
            "queue_position": position,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "error_message": job.error_message,
            "retry_count": job.retry_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting job status: {str(e)}"
        )

@router.post("/cancel/{idea_id}")
async def cancel_job(idea_id: str):
    """
    Annuler un job en attente
    """
    try:
        queue_service = QueueService()
        
        # Récupérer le job
        job = await queue_service.get_job_by_idea(idea_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No job found for idea {idea_id}"
            )
        
        await queue_service.cancel_job(job.job_id)
        
        # Mettre à jour l'idée
        ideas_collection = get_ideas_collection()
        await ideas_collection.update_one(
            {"id": idea_id},
            {"$set": {
                "status": "validated",
                "current_step": "Génération annulée"
            }}
        )
        
        return {
            "success": True,
            "message": "Job cancelled",
            "job_id": job.job_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling job: {str(e)}"
        )
