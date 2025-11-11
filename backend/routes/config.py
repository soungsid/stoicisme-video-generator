from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from services.youtube_config_service import YoutubeConfigService
from services.elevenlabs_config_service import ElevenLabsConfigService
from services.llm_config_service import LlmConfigService
import os

router = APIRouter()

class YouTubeCredentials(BaseModel):
    client_id: str
    client_secret: str

@router.post("/youtube")
async def update_youtube_config(credentials: YouTubeCredentials):
    """
    Mettre à jour les credentials YouTube
    """
    try:
        service = YoutubeConfigService()
        result = await service.update_credentials(
            client_id=credentials.client_id,
            client_secret=credentials.client_secret
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating YouTube config: {str(e)}"
        )

@router.get("/elevenlabs/keys-details")
async def get_elevenlabs_keys_details():
    """
    Récupérer les détails de toutes les clés ElevenLabs configurées
    """
    try:
        service = ElevenLabsConfigService()
        return await service.get_keys_details()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ElevenLabs keys details: {str(e)}"
        )

@router.get("/elevenlabs/stats")
async def get_elevenlabs_stats():
    """
    Récupérer les statistiques d'utilisation ElevenLabs
    """
    try:
        service = ElevenLabsConfigService()
        return await service.get_stats()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ElevenLabs stats: {str(e)}"
        )

@router.get("/elevenlabs")
async def get_elevenlabs_config():
    """
    Récupérer la configuration ElevenLabs
    """
    try:
        service = ElevenLabsConfigService()
        return await service.get_config()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ElevenLabs config: {str(e)}"
        )

@router.get("/llm")
async def get_llm_config():
    """
    Récupérer la configuration LLM
    """
    try:
        service = LlmConfigService()
        return await service.get_config()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching LLM config: {str(e)}"
        )

@router.get("/youtube/stats")
async def get_youtube_stats():
    """
    Récupérer les statistiques d'utilisation YouTube
    """
    try:
        from database import get_videos_collection, get_config_collection
        from datetime import datetime
        
        videos_collection = get_videos_collection()
        config_collection = get_config_collection()
        
        # Vérifier si YouTube est authentifié
        youtube_config = await config_collection.find_one({"type": "youtube"})
        is_authenticated = youtube_config and youtube_config.get("is_authenticated", False)
        
        # Compter les vidéos uploadées aujourd'hui
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        uploads_today = await videos_collection.count_documents({
            "uploaded_at": {"$gte": today_start}
        })
        
        # Compter total de vidéos uploadées
        total_uploads = await videos_collection.count_documents({
            "youtube_video_id": {"$exists": True, "$ne": None}
        })
        
        # Compter vidéos en attente d'upload
        pending_uploads = await videos_collection.count_documents({
            "youtube_video_id": {"$exists": False}
        })
        
        return {
            "authenticated": is_authenticated,
            "uploads_today": uploads_today,
            "total_uploads": total_uploads,
            "pending_uploads": pending_uploads,
            "quota_info": {
                "daily_limit": 6,
                "note": "YouTube API quota: 10,000 unités/jour. Upload = ~1600 unités"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching YouTube stats: {str(e)}"
        )

