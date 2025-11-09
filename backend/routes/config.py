from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database import get_config_collection
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
        config_collection = get_config_collection()
        
        await config_collection.update_one(
            {"type": "youtube"},
            {
                "$set": {
                    "type": "youtube",
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                    "is_authenticated": False
                }
            },
            upsert=True
        )
        
        return {"success": True, "message": "YouTube credentials updated"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating YouTube config: {str(e)}"
        )

@router.get("/elevenlabs/stats")
async def get_elevenlabs_stats():
    """
    Récupérer les statistiques d'utilisation ElevenLabs
    """
    try:
        from services.elevenlabs_service import ElevenLabsService
        from database import get_scripts_collection
        from datetime import datetime, timedelta
        
        # Compter les caractères générés aujourd'hui
        scripts_collection = get_scripts_collection()
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Compter les scripts générés aujourd'hui
        scripts_today = await scripts_collection.count_documents({
            "created_at": {"$gte": today_start}
        })
        
        # Estimer les caractères (moyenne ~200 caractères par script)
        estimated_chars_today = scripts_today * 200
        
        # Configuration des clés
        configured_keys = []
        for i in range(1, 6):
            key = os.getenv(f"ELEVENLABS_API_KEY{i}")
            if key and key.startswith("sk_"):
                configured_keys.append(i)
        
        return {
            "keys_configured": len(configured_keys),
            "scripts_generated_today": scripts_today,
            "estimated_chars_today": estimated_chars_today,
            "quota_info": {
                "estimated_chars_per_script": 200,
                "free_tier_monthly": 10000,
                "note": "Les quotas exacts nécessitent l'API ElevenLabs"
            },
            "rotation_status": {
                "enabled": len(configured_keys) > 1,
                "total_keys": len(configured_keys)
            }
        }
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
        # Compter les clés disponibles
        api_keys = []
        for i in range(1, 6):
            key = os.getenv(f"ELEVENLABS_API_KEY{i}")
            if key and key.startswith("sk_"):
                api_keys.append({
                    "index": i,
                    "configured": True,
                    "key_preview": key[:10] + "..." if len(key) > 10 else key
                })
            else:
                api_keys.append({
                    "index": i,
                    "configured": False
                })
        
        voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        voice_name = os.getenv("ELEVENLABS_VOICE_NAME")
        
        return {
            "api_keys": api_keys,
            "voice_id": voice_id,
            "voice_name": voice_name,
            "total_keys": len([k for k in api_keys if k["configured"]]),
            "voice_settings": {
                "current_voice_id": voice_id,
                "current_voice_name": voice_name,
                "can_change": True
            }
        }
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
        provider = os.getenv("AI_PROVIDER", "deepseek")
        
        config = {
            "provider": provider,
            "deepseek": {
                "configured": bool(os.getenv("DEEPSEEK_API_KEY")),
                "model": os.getenv("DEEPSEEK_MODEL")
            },
            "openai": {
                "configured": bool(os.getenv("OPENAI_API_KEY")) and os.getenv("OPENAI_API_KEY") != "your-openai-api-key-here",
                "model": os.getenv("OPENAI_MODEL")
            },
            "gemini": {
                "configured": bool(os.getenv("GEMINI_API_KEY")) and os.getenv("GEMINI_API_KEY") != "your-gemini-api-key-here",
                "model": os.getenv("GEMINI_MODEL")
            }
        }
        
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching LLM config: {str(e)}"
        )
