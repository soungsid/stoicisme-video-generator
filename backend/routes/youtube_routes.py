from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from models import YouTubeConfig
from database import get_config_collection, get_videos_collection, get_ideas_collection
from services.youtube_service import YouTubeService
from datetime import datetime
import os

router = APIRouter()

@router.get("/auth/url")
async def get_auth_url():
    """
    Générer l'URL d'authentification OAuth YouTube
    """
    try:
        youtube_service = YouTubeService()
        auth_url = youtube_service.get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating auth URL: {str(e)}"
        )

@router.get("/oauth/callback")
async def oauth_callback(code: str):
    """
    Callback OAuth YouTube
    """
    try:
        youtube_service = YouTubeService()
        await youtube_service.handle_oauth_callback(code)
        
        return RedirectResponse(url="http://localhost:3000/config?auth=success")
    except Exception as e:
        return RedirectResponse(url="http://localhost:3000/config?auth=error")

@router.get("/config", response_model=YouTubeConfig)
async def get_youtube_config():
    """
    Récupérer la configuration YouTube
    """
    try:
        config_collection = get_config_collection()
        config = await config_collection.find_one({"type": "youtube"})
        
        if not config:
            return YouTubeConfig(is_authenticated=False)
        
        # Ne pas retourner les tokens sensibles
        return YouTubeConfig(
            client_id=config.get("client_id"),
            is_authenticated=config.get("is_authenticated", False)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching YouTube config: {str(e)}"
        )

@router.get("/channel-info")
async def get_channel_info():
    """
    Récupérer les informations de la chaîne YouTube connectée
    """
    try:
        youtube_service = YouTubeService()
        channel_info = await youtube_service.get_channel_info()
        return channel_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching channel info: {str(e)}"
        )

@router.post("/upload/{video_id}")
async def upload_video(video_id: str, title: str = None, description: str = None, tags: list = None):
    """
    Uploader une vidéo sur YouTube
    """
    try:
        videos_collection = get_videos_collection()
        video = await videos_collection.find_one({"id": video_id}, {"_id": 0})
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found"
            )
        
        # Générer une description optimisée si non fournie
        if not description:
            from agents.youtube_description_agent import YouTubeDescriptionAgent
            from database import get_scripts_collection
            
            scripts_collection = get_scripts_collection()
            script = await scripts_collection.find_one({"id": video["script_id"]}, {"_id": 0})
            
            if script:
                agent = YouTubeDescriptionAgent()
                description = await agent.generate_description(
                    title=title or video["title"],
                    script=script.get("original_script", ""),
                    keywords=script.get("keywords", [])
                )
        
        youtube_service = YouTubeService()
        youtube_video_id, youtube_url = await youtube_service.upload_video(
            video_path=video["video_path"],
            title=title or video["title"],
            description=description or f"Vidéo sur le stoïcisme: {video['title']}",
            tags=tags or ["stoicisme", "philosophie", "sagesse"],
            category_id="22"  # People & Blogs
        )
        
        # Mettre à jour la vidéo
        await videos_collection.update_one(
            {"id": video_id},
            {
                "$set": {
                    "youtube_video_id": youtube_video_id,
                    "youtube_url": youtube_url,
                    "uploaded_at": datetime.now()
                }
            }
        )
        
        # Mettre à jour l'idée
        ideas_collection = get_ideas_collection()
        from models import IdeaStatus
        await ideas_collection.update_one(
            {"id": video["idea_id"]},
            {"$set": {"status": IdeaStatus.UPLOADED}}
        )
        
        return {
            "success": True,
            "youtube_video_id": youtube_video_id,
            "youtube_url": youtube_url,
            "description_generated": description
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading video: {str(e)}"
        )

@router.patch("/update/{youtube_video_id}")
async def update_youtube_video(
    youtube_video_id: str,
    title: str = None,
    description: str = None,
    tags: list = None
):
    """
    Mettre à jour les métadonnées d'une vidéo YouTube déjà uploadée
    """
    try:
        youtube_service = YouTubeService()
        result = await youtube_service.update_video_metadata(
            youtube_video_id=youtube_video_id,
            title=title,
            description=description,
            tags=tags
        )
        return {"success": True, "message": "Video metadata updated", "result": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating video: {str(e)}"
        )
