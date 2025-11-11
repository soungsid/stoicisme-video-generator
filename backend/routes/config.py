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
        service = YoutubeConfigService()
        return await service.get_stats()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching YouTube stats: {str(e)}"
        )

