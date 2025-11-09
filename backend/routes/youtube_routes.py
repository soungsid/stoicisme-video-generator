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

@router.post("/disconnect")
async def disconnect_youtube():
    """
    Déconnecter le compte YouTube actuel
    """
    try:
        from database import get_config_collection
        
        config_collection = get_config_collection()
        
        # Supprimer la configuration YouTube
        await config_collection.delete_one({"type": "youtube"})
        
        return {
            "success": True,
            "message": "YouTube account disconnected successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disconnecting YouTube: {str(e)}"
        )

@router.post("/schedule/{video_id}")
async def schedule_video(video_id: str, publish_date: str):
    """
    Planifier la publication d'une vidéo
    """
    try:
        from datetime import datetime
        from database import get_videos_collection
        
        videos_collection = get_videos_collection()
        
        # Parser la date
        scheduled_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
        
        # Mettre à jour la vidéo
        result = await videos_collection.update_one(
            {"id": video_id},
            {
                "$set": {
                    "scheduled_publish_date": scheduled_date,
                    "is_scheduled": True
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found"
            )
        
        return {
            "success": True,
            "message": "Video scheduled successfully",
            "scheduled_date": scheduled_date.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling video: {str(e)}"
        )

@router.post("/schedule/bulk")
async def schedule_bulk(data: dict):
    """
    Planifier plusieurs vidéos en masse
    Body: {
        "start_date": "2025-11-09",
        "videos_per_day": 2,
        "publish_times": ["09:00", "18:00"]
    }
    """
    try:
        from datetime import datetime, timedelta
        from database import get_videos_collection
        
        start_date = data.get("start_date")
        videos_per_day = data.get("videos_per_day", 2)
        publish_times = data.get("publish_times", [])
        
        videos_collection = get_videos_collection()
        
        # Récupérer les vidéos non publiées
        unpublished_videos = await videos_collection.find({
            "youtube_video_id": {"$exists": False}
        }).to_list(length=1000)
        
        if not unpublished_videos:
            return {
                "success": True,
                "message": "No videos to schedule",
                "scheduled_count": 0
            }
        
        # Parser la date de début
        current_date = datetime.fromisoformat(start_date)
        
        # Planifier les vidéos
        scheduled_count = 0
        time_index = 0
        
        for video in unpublished_videos:
            # Déterminer l'heure de publication
            publish_time = publish_times[time_index % len(publish_times)]
            hour, minute = map(int, publish_time.split(':'))
            
            # Créer la date complète
            scheduled_datetime = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Mettre à jour la vidéo
            await videos_collection.update_one(
                {"id": video["id"]},
                {
                    "$set": {
                        "scheduled_publish_date": scheduled_datetime,
                        "is_scheduled": True
                    }
                }
            )
            
            scheduled_count += 1
            time_index += 1
            
            # Si on a planifié videos_per_day vidéos, passer au jour suivant
            if time_index % (videos_per_day * len(publish_times)) == 0:
                current_date += timedelta(days=1)
        
        return {
            "success": True,
            "message": f"{scheduled_count} videos scheduled successfully",
            "scheduled_count": scheduled_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling videos: {str(e)}"
        )

@router.delete("/schedule/{video_id}")
async def unschedule_video(video_id: str):
    """
    Annuler la planification d'une vidéo
    """
    try:
        from database import get_videos_collection
        
        videos_collection = get_videos_collection()
        
        result = await videos_collection.update_one(
            {"id": video_id},
            {
                "$set": {
                    "is_scheduled": False
                },
                "$unset": {
                    "scheduled_publish_date": ""
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found"
            )
        
        return {
            "success": True,
            "message": "Video unscheduled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unscheduling video: {str(e)}"
        )
