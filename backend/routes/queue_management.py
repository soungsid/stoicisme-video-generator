from fastapi import APIRouter, HTTPException
from services.publication_service import PublicationService
import traceback

router = APIRouter()

# Instance globale du service de publication
publication_service = PublicationService()

@router.get("/status")
async def get_queue_status():
    """
    Obtenir le statut actuel de la queue de publication
    
    Returns:
        Statistiques sur les vidéos planifiées et publiées
    """
    try:
        status = await publication_service.get_queue_status()
        return status
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error getting queue status: {str(e)}"
        )

@router.post("/process")
async def process_queue_manually():
    """
    Déclencher manuellement le traitement de la queue
    
    Utile pour forcer la publication des vidéos sans attendre
    le worker automatique.
    
    Returns:
        Résultats du traitement (nombre de vidéos publiées, etc.)
    """
    try:
        print("\n🔧 Traitement manuel de la queue déclenché")
        result = await publication_service.process_queue()
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing queue: {str(e)}"
        )

@router.post("/start")
async def start_worker():
    """
    Démarrer le worker de publication automatique
    
    Note: Cette route démarre le flag is_running mais le worker
    réel doit être lancé via supervisor ou manuellement.
    """
    try:
        if publication_service.is_running:
            return {
                "success": False,
                "message": "Worker is already running"
            }
        
        publication_service.is_running = True
        
        return {
            "success": True,
            "message": "Worker started (flag set). Ensure the worker process is running."
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error starting worker: {str(e)}"
        )

@router.post("/stop")
async def stop_worker():
    """
    Arrêter le worker de publication automatique
    
    Note: Cette route arrête le flag is_running. Pour arrêter
    le processus réel, utilisez supervisor.
    """
    try:
        if not publication_service.is_running:
            return {
                "success": False,
                "message": "Worker is not running"
            }
        
        publication_service.is_running = False
        
        return {
            "success": True,
            "message": "Worker stopped (flag unset)"
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error stopping worker: {str(e)}"
        )

@router.get("/scheduled-videos")
async def get_scheduled_videos():
    """
    Obtenir la liste des vidéos planifiées
    
    Returns:
        Liste des vidéos avec leur date de publication programmée
    """
    try:
        videos = await publication_service.get_scheduled_videos()
        
        # Formater pour l'affichage
        formatted_videos = []
        for video in videos:
            formatted_videos.append({
                "id": video.get("id"),
                "title": video.get("title"),
                "scheduled_date": video.get("scheduled_publish_date").isoformat() if video.get("scheduled_publish_date") else None,
                "video_path": video.get("video_path")
            })
        
        return {
            "count": len(formatted_videos),
            "videos": formatted_videos
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error getting scheduled videos: {str(e)}"
        )
