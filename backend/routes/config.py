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
            "total_keys": len([k for k in api_keys if k["configured"]])
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
