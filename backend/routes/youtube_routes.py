from fastapi import APIRouter, HTTPException, status, Request, Body
from fastapi.responses import RedirectResponse
from numpy import empty
from models import (
    YouTubeConfig, ScheduleVideoRequest, BulkScheduleRequest,
    UploadVideoRequest, UpdateVideoMetadataRequest
)
from database import get_config_collection, get_videos_collection, get_ideas_collection
from services.youtube_service import YouTubeService
from datetime import datetime
import os
import traceback
from api import FRONTEND_URL

router = APIRouter()

@router.get("/auth/url")
async def get_auth_url():
    """
    Générer l'URL d'authentification OAuth YouTube
    """
    try:
        print("je passe ici")
        youtube_service = YouTubeService()
        auth_url = youtube_service.get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        print("❌ Error generating auth URL:")
        traceback.print_exc()  # ← affiche la pile complète dans la console
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
        
        return RedirectResponse(url=f"{FRONTEND_URL}/config?auth=success")
    except Exception as e:
        traceback.print_exc()  # ← affiche la pile complète dans la console
        return RedirectResponse(url=f"{FRONTEND_URL}/config?auth=error")

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
async def upload_video_to_youtube(video_id: str):
    """
    Uploader une vidéo sur YouTube
    
    Le service YouTube récupère automatiquement toutes les informations
    nécessaires depuis MongoDB (vidéo, script, description, etc.)
    """
    try:
        youtube_service = YouTubeService()
        
        print(f"📤 Upload de la vidéo {video_id} sur YouTube...")
        result = await youtube_service.upload_video(video_id=video_id)
        
        print("✅ Upload réussi!")
        
        # Mettre à jour le statut de l'idée si nécessaire
        from database import get_videos_collection, get_ideas_collection
        from models import IdeaStatus
        
        videos_collection = get_videos_collection()
        video = await videos_collection.find_one({"id": video_id}, {"_id": 0, "idea_id": 1})
        
        if video and video.get("idea_id"):
            ideas_collection = get_ideas_collection()
            await ideas_collection.update_one(
                {"id": video["idea_id"]},
                {"$set": {"status": IdeaStatus.UPLOADED}}
            )
        
        return {
            "success": True,
            "youtube_video_id": result["youtube_video_id"],
            "youtube_url": result["youtube_url"],
            "uploaded_at": result["uploaded_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
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
        print("Mise à jour de la video")
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
        result = await config_collection.delete_one({"type": "youtube"})
        
        print(f"✅ YouTube tokens cleared: {result.deleted_count} document(s) deleted")
        
        return {
            "success": True,
            "message": "YouTube account disconnected successfully",
            "tokens_cleared": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disconnecting YouTube: {str(e)}"
        )

@router.post("/clear-tokens")
async def clear_youtube_tokens():
    """
    Nettoyer les tokens YouTube corrompus (utile en cas de problème OAuth)
    """
    try:
        from database import get_config_collection
        
        config_collection = get_config_collection()
        
        # Supprimer tous les tokens YouTube
        result = await config_collection.delete_many({"type": "youtube"})
        
        print(f"✅ All YouTube tokens cleared: {result.deleted_count} document(s) deleted")
        
        return {
            "success": True,
            "message": "All YouTube tokens cleared. Please re-authenticate.",
            "tokens_cleared": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing tokens: {str(e)}"
        )

@router.post("/schedule/bulk")
async def schedule_bulk(request: BulkScheduleRequest):
    """
    Planifier plusieurs vidéos en masse
    
    Args:
        request: Configuration de planification
            - start_date: Date de début (YYYY-MM-DD)
            - videos_per_day: Nombre de vidéos par jour
            - publish_times: Heures de publication (ex: ["09:00", "18:00"])
    
    Returns:
        Nombre de vidéos planifiées
    
    Note: Les dates sont en UTC par défaut. Les heures dans publish_times
    sont interprétées comme UTC.
    """
    try:
        from datetime import datetime, timedelta
        from database import get_videos_collection
        print("📅 Planification en masse démarrée")
        
        start_date = request.start_date
        videos_per_day = request.videos_per_day
        publish_times = request.publish_times
        
        videos_collection = get_videos_collection()
        
        # Récupérer les vidéos non publiées
        unpublished_videos = await videos_collection.find({
            "$or": [
                {"youtube_video_id": {"$exists": False}},
                {"youtube_video_id": None}
            ]
        }).to_list(length=1000)
        print(f"{len(unpublished_videos)} videos non encore publiées")
        
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
            # Déterminer l'heure de publication (cycle à travers publish_times)
            publish_time = publish_times[time_index % len(publish_times)]
            hour, minute = map(int, publish_time.split(':'))
            
            # Créer la date complète avec l'heure
            scheduled_datetime = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            print(f"📌 Vidéo '{video.get('title', 'Sans titre')}' → {scheduled_datetime.isoformat()}")
            
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
            
            # Passer au jour suivant après avoir utilisé toutes les heures de publication
            # Exemple: avec ["09:00", "18:00"], on change de jour après 2 vidéos
            if time_index % len(publish_times) == 0:
                current_date += timedelta(days=1)
                print(f"📆 Passage au jour suivant: {current_date.strftime('%Y-%m-%d')}")
        
        print(f"✅ {scheduled_count} vidéos planifiées avec succès")
        
        return {
            "success": True,
            "message": f"{scheduled_count} videos scheduled successfully",
            "scheduled_count": scheduled_count,
            "start_date": start_date,
            "timezone": "UTC"
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling videos: {str(e)}"
        )

@router.post("/schedule/{video_id}")
async def schedule_video(video_id: str, request: ScheduleVideoRequest):
    """
    Planifier la publication d'une vidéo
    
    Args:
        video_id: ID de la vidéo
        request: Données de planification avec publish_date
    
    Returns:
        Confirmation de planification avec la date programmée
    
    Note: Les dates sont en UTC par défaut. Pour utiliser un fuseau local,
    ajoutez le offset dans la date (ex: 2025-11-10T09:00:00+01:00)
    """
    try:
        from datetime import datetime
        from database import get_videos_collection
        
        videos_collection = get_videos_collection()
        
        # Parser la date
        scheduled_date = datetime.fromisoformat(request.publish_date.replace('Z', '+00:00'))
        
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
        
        print(f"✅ Video {video_id} scheduled for {scheduled_date.isoformat()}")
        
        return {
            "success": True,
            "message": "Video scheduled successfully",
            "scheduled_date": scheduled_date.isoformat(),
            "timezone": "UTC"
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling video: {str(e)}"
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
