from fastapi import APIRouter, HTTPException, status, Request, Body
from fastapi.responses import RedirectResponse
from numpy import empty
from models import (
    YouTubeConfig, ScheduleVideoRequest, BulkScheduleRequest,
    UploadVideoRequest, UpdateVideoMetadataRequest
)
from database import get_config_collection, get_videos_collection, get_ideas_collection
from services.youtube_service import YouTubeService
from services.youtube_scheduling_service import YoutubeSchedulingService
from services.youtube_thumbnail_service import YouTubeThumbnailService
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
    except Exception:
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
    
    Le service YouTube gère automatiquement:
    - Récupération des informations depuis MongoDB
    - Upload sur YouTube
    - Mise à jour de la vidéo et de l'idée dans MongoDB
    """
    try:
        youtube_service = YouTubeService()
        
        print(f"📤 Upload de la vidéo {video_id} sur YouTube...")
        result = await youtube_service.upload_video(video_id=video_id)
        
        print("✅ Upload réussi!")
        
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
        scheduling_service = YoutubeSchedulingService()
        
        result = await scheduling_service.bulk_schedule(
            start_date=request.start_date,
            videos_per_day=request.videos_per_day,
            publish_times=request.publish_times
        )
        
        return result
        
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
        scheduling_service = YoutubeSchedulingService()
        
        result = await scheduling_service.schedule_video(
            video_id=video_id,
            publish_date=request.publish_date
        )
        
        return {
            "success": True,
            "message": "Video scheduled successfully",
            "scheduled_date": result["scheduled_date"],
            "timezone": result["timezone"]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
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
        scheduling_service = YoutubeSchedulingService()
        
        result = await scheduling_service.unschedule_video(video_id=video_id)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unscheduling video: {str(e)}"
        )

# ===== ROUTES POUR LA GESTION DES THUMBNAILS =====

@router.post("/thumbnail/update/{youtube_video_id}")
async def update_youtube_thumbnail(
    youtube_video_id: str,
    thumbnail_path: str
):
    """
    Mettre à jour le thumbnail d'une vidéo YouTube
    
    Args:
        youtube_video_id: ID de la vidéo YouTube
        thumbnail_path: Chemin vers le fichier thumbnail
    """
    try:
        thumbnail_service = YouTubeThumbnailService()
        
        print(f"🖼️  Mise à jour du thumbnail pour la vidéo {youtube_video_id}...")
        result = await thumbnail_service.update_thumbnail(
            youtube_video_id=youtube_video_id,
            thumbnail_path=thumbnail_path
        )
        
        print("✅ Thumbnail mis à jour avec succès!")
        
        return {
            "success": True,
            "message": "Thumbnail updated successfully",
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating thumbnail: {str(e)}"
        )

@router.post("/thumbnail/update-by-video/{video_id}")
async def update_thumbnail_by_video_id(video_id: str):
    """
    Mettre à jour le thumbnail d'une vidéo YouTube en utilisant l'ID de la vidéo locale
    
    Args:
        video_id: ID de la vidéo dans la base de données
    """
    try:
        thumbnail_service = YouTubeThumbnailService()
        
        print(f"🖼️  Mise à jour du thumbnail pour la vidéo locale {video_id}...")
        result = await thumbnail_service.update_thumbnail_by_video_id(video_id=video_id)
        
        print("✅ Thumbnail mis à jour avec succès!")
        
        return {
            "success": True,
            "message": "Thumbnail updated successfully",
            "result": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating thumbnail: {str(e)}"
        )

@router.get("/thumbnail/info/{youtube_video_id}")
async def get_thumbnail_info(youtube_video_id: str):
    """
    Récupérer les informations sur les thumbnails d'une vidéo YouTube
    
    Args:
        youtube_video_id: ID de la vidéo YouTube
    """
    try:
        thumbnail_service = YouTubeThumbnailService()
        
        print(f"ℹ️  Récupération des infos thumbnail pour la vidéo {youtube_video_id}...")
        result = await thumbnail_service.get_thumbnail_info(youtube_video_id=youtube_video_id)
        
        return {
            "success": True,
            "result": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting thumbnail info: {str(e)}"
        )

@router.post("/thumbnail/batch-update")
async def batch_update_thumbnails(video_ids: list):
    """
    Mettre à jour les thumbnails de plusieurs vidéos en lot
    
    Args:
        video_ids: Liste des IDs de vidéos locales
    """
    try:
        thumbnail_service = YouTubeThumbnailService()
        
        print(f"🖼️  Mise à jour en lot des thumbnails pour {len(video_ids)} vidéos...")
        result = await thumbnail_service.batch_update_thumbnails(video_ids=video_ids)
        
        return {
            "success": True,
            "message": f"Batch thumbnail update completed: {len(result['successful'])} successful, {len(result['failed'])} failed",
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch thumbnail update: {str(e)}"
        )
