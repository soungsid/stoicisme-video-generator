"""
Service de gestion de la queue de génération vidéo
"""
from datetime import datetime
from typing import Optional, List
from models import VideoJob, JobStatus, IdeaStatus
from database import get_queue_collection, get_ideas_collection
import os

class QueueService:
    """Gestionnaire de queue pour les jobs de génération vidéo"""
    
    def __init__(self):
        self.max_concurrent = int(os.getenv("MAX_CONCURRENT_VIDEO_JOBS", "2"))
        self.queue_collection = get_queue_collection()
        self.ideas_collection = get_ideas_collection()
    
    async def add_job(self, idea_id: str, start_from: str = "script", priority: int = 0) -> VideoJob:
        """
        Ajouter un job à la queue
        """
        # Vérifier si un job existe déjà pour cette idée
        existing_job = await self.queue_collection.find_one({
            "idea_id": idea_id,
            "status": {"$in": [JobStatus.QUEUED, JobStatus.PROCESSING]}
        })
        
        if existing_job:
            return VideoJob(**existing_job)
        
        # Créer un nouveau job
        job = VideoJob(
            idea_id=idea_id,
            start_from=start_from,
            priority=priority,
            status=JobStatus.QUEUED
        )
        
        await self.queue_collection.insert_one(job.model_dump())
        
        # Mettre à jour le statut de l'idée
        await self.ideas_collection.update_one(
            {"id": idea_id},
            {"$set": {
                "status": IdeaStatus.QUEUED,
                "current_step": "En attente dans la queue"
            }}
        )
        
        print(f"✅ Job added to queue: {job.job_id} for idea {idea_id}")
        return job
    
    async def get_next_job(self) -> Optional[VideoJob]:
        """
        Récupérer le prochain job à traiter
        Priorise par: priority DESC, created_at ASC
        """
        job_data = await self.queue_collection.find_one_and_update(
            {"status": JobStatus.QUEUED},
            {
                "$set": {
                    "status": JobStatus.PROCESSING,
                    "started_at": datetime.now()
                }
            },
            sort=[("priority", -1), ("created_at", 1)],
            return_document=True
        )
        
        if job_data:
            return VideoJob(**job_data)
        return None
    
    async def get_processing_count(self) -> int:
        """Compter le nombre de jobs en cours de traitement"""
        count = await self.queue_collection.count_documents({
            "status": JobStatus.PROCESSING
        })
        return count
    
    async def can_process_more(self) -> bool:
        """Vérifier si on peut traiter plus de jobs"""
        processing_count = await self.get_processing_count()
        return processing_count < self.max_concurrent
    
    async def complete_job(self, job_id: str):
        """Marquer un job comme complété"""
        await self.queue_collection.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": JobStatus.COMPLETED,
                    "completed_at": datetime.now()
                }
            }
        )
        print(f"✅ Job completed: {job_id}")
    
    async def fail_job(self, job_id: str, error_message: str):
        """Marquer un job comme échoué"""
        job_data = await self.queue_collection.find_one({"job_id": job_id})
        
        if not job_data:
            return
        
        job = VideoJob(**job_data)
        retry_count = job.retry_count + 1
        
        # Si on peut retry, remettre en queue
        if retry_count < job.max_retries:
            await self.queue_collection.update_one(
                {"job_id": job_id},
                {
                    "$set": {
                        "status": JobStatus.QUEUED,
                        "retry_count": retry_count,
                        "error_message": error_message,
                        "started_at": None
                    }
                }
            )
            print(f"⚠️ Job {job_id} failed, retry {retry_count}/{job.max_retries}")
        else:
            # Max retries atteint
            await self.queue_collection.update_one(
                {"job_id": job_id},
                {
                    "$set": {
                        "status": JobStatus.FAILED,
                        "completed_at": datetime.now(),
                        "error_message": error_message
                    }
                }
            )
            print(f"❌ Job {job_id} failed permanently after {retry_count} retries")
    
    async def cancel_job(self, job_id: str):
        """Annuler un job"""
        await self.queue_collection.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": JobStatus.CANCELLED,
                    "completed_at": datetime.now()
                }
            }
        )
        print(f"⚠️ Job cancelled: {job_id}")
    
    async def get_job_by_idea(self, idea_id: str) -> Optional[VideoJob]:
        """Récupérer le job d'une idée"""
        job_data = await self.queue_collection.find_one(
            {"idea_id": idea_id},
            sort=[("created_at", -1)]
        )
        
        if job_data:
            return VideoJob(**job_data)
        return None
    
    async def get_queue_position(self, idea_id: str) -> Optional[int]:
        """
        Obtenir la position d'un job dans la queue
        Retourne None si pas en queue, sinon la position (1-indexed)
        """
        job = await self.get_job_by_idea(idea_id)
        
        if not job or job.status != JobStatus.QUEUED:
            return None
        
        # Compter combien de jobs sont avant celui-ci
        count = await self.queue_collection.count_documents({
            "status": JobStatus.QUEUED,
            "$or": [
                {"priority": {"$gt": job.priority}},
                {
                    "priority": job.priority,
                    "created_at": {"$lt": job.created_at}
                }
            ]
        })
        
        return count + 1
    
    async def get_queue_stats(self) -> dict:
        """Statistiques de la queue"""
        queued = await self.queue_collection.count_documents({"status": JobStatus.QUEUED})
        processing = await self.queue_collection.count_documents({"status": JobStatus.PROCESSING})
        completed_today = await self.queue_collection.count_documents({
            "status": JobStatus.COMPLETED,
            "completed_at": {"$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
        })
        
        return {
            "queued": queued,
            "processing": processing,
            "completed_today": completed_today,
            "max_concurrent": self.max_concurrent,
            "available_slots": max(0, self.max_concurrent - processing)
        }
