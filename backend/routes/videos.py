from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from models import Video, IdeaStatus
from database import get_videos_collection, get_scripts_collection, get_ideas_collection
from services.video_service import VideoService
import os

router = APIRouter()

@router.post("/generate/{script_id}", response_model=Video)
async def generate_video(script_id: str, background_tasks: BackgroundTasks):
    """
    Générer une vidéo complète avec audio et sous-titres
    
    Le service VideoService gère automatiquement:
    - Récupération du script et de l'idée depuis MongoDB
    - Validation du statut de l'idée
    - Génération de la vidéo
    """
    try:
        scripts_collection = get_scripts_collection()
        script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
        
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {script_id} not found"
            )
        
        # Vérifier le statut de l'idée
        idea_id = script.get("idea_id")
        if not idea_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Script has no associated idea"
            )
        
        ideas_collection = get_ideas_collection()
        idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
        
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        if idea["status"] != IdeaStatus.AUDIO_GENERATED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio must be generated before video generation"
            )
        
        # Générer la vidéo (le service récupère script et idea lui-même)
        video_service = VideoService()
        video = await video_service.generate_video(script_id=script_id)
        
        # Sauvegarder la vidéo
        videos_collection = get_videos_collection()
        await videos_collection.insert_one(video.model_dump())
        
        # Mettre à jour le statut de l'idée
        await ideas_collection.update_one(
            {"id": idea_id},
            {"$set": {"status": IdeaStatus.VIDEO_GENERATED}}
        )
        
        return video
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating video: {str(e)}"
        )

@router.get("/by-idea/{idea_id}", response_model=Video)
async def get_video_by_idea(idea_id: str):
    """
    Récupérer la vidéo pour une idée
    """
    try:
        videos_collection = get_videos_collection()
        video = await videos_collection.find_one({"idea_id": idea_id}, {"_id": 0})
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video for idea {idea_id} not found"
            )
        
        return video
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching video: {str(e)}"
        )

@router.get("/{video_id}/details")
async def get_video_details(video_id: str):
    """
    Récupérer les détails complets d'une vidéo avec toutes les informations enrichies
    
    Retourne:
    - Informations de base (titre, description, tags)
    - Chemin de la vidéo et thumbnail
    - Durée de la vidéo
    - Informations YouTube si publiée (ID, URL, date d'upload)
    - Informations de planification si planifiée
    - Statut de publication
    - Métadonnées du script et de l'idée associés
    """
    try:
        videos_collection = get_videos_collection()
        video = await videos_collection.find_one({"id": video_id}, {"_id": 0})
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found"
            )
        
        # Récupérer les informations du script associé
        script = None
        if video.get("script_id"):
            scripts_collection = get_scripts_collection()
            script = await scripts_collection.find_one(
                {"id": video["script_id"]}, 
                {"_id": 0, "title": 1, "original_script": 1, "created_at": 1}
            )
        
        # Récupérer les informations de l'idée associée
        idea = None
        if video.get("idea_id"):
            ideas_collection = get_ideas_collection()
            idea = await ideas_collection.find_one(
                {"id": video["idea_id"]}, 
                {"_id": 0, "title": 1, "keywords": 1, "status": 1, "created_at": 1}
            )
        
        # Construire la réponse enrichie
        details = {
            # Informations de base
            "id": video.get("id"),
            "title": video.get("title"),
            "description": video.get("description", ""),
            "tags": video.get("tags", []),
            
            # Fichiers
            "video_path": video.get("video_path"),
            "thumbnail_path": video.get("thumbnail_path"),
            "video_url": f"/media/videos/{os.path.basename(video.get('video_path', ''))}" if video.get("video_path") else None,
            "thumbnail_url": f"/media/thumbnails/{os.path.basename(video.get('thumbnail_path', ''))}" if video.get("thumbnail_path") else None,
            
            # Métadonnées vidéo
            "duration_seconds": video.get("duration_seconds"),
            "video_type": video.get("video_type"),
            "created_at": video.get("created_at"),
            
            # Informations YouTube
            "youtube_video_id": video.get("youtube_video_id"),
            "youtube_url": video.get("youtube_url"),
            "uploaded_at": video.get("uploaded_at"),
            
            # Planification
            "is_scheduled": video.get("is_scheduled", False),
            "scheduled_publish_date": video.get("scheduled_publish_date"),
            
            # Erreurs éventuelles
            "publication_error": video.get("publication_error"),
            "publication_error_at": video.get("publication_error_at"),
            
            # Statut de publication
            "publication_status": "published" if video.get("youtube_video_id") else (
                "scheduled" if video.get("is_scheduled") else (
                    "error" if video.get("publication_error") else "draft"
                )
            ),
            
            # Informations associées
            "script": script,
            "idea": idea,
            
            # IDs de référence
            "script_id": video.get("script_id"),
            "audio_id": video.get("audio_id"),
            "idea_id": video.get("idea_id")
        }
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching video details: {str(e)}"
        )

@router.get("/{video_id}", response_model=Video)
async def get_video(video_id: str):
    """
    Récupérer une vidéo spécifique (format standard)
    """
    try:
        videos_collection = get_videos_collection()
        video = await videos_collection.find_one({"id": video_id}, {"_id": 0})
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found"
            )
        
        return video
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching video: {str(e)}"
        )

@router.get("/")
async def list_videos(
    status_filter: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """
    Lister toutes les vidéos générées avec tri et filtrage
    status_filter: 'uploaded', 'scheduled', 'pending'
    sort_by: 'created_at', 'title', 'scheduled_publish_date'
    sort_order: 'asc', 'desc'
    """
    try:
        videos_collection = get_videos_collection()
        
        # Construire le filtre
        query = {}
        if status_filter:
            if status_filter == "uploaded":
                query["youtube_video_id"] = {"$exists": True, "$ne": None}
            elif status_filter == "scheduled":
                query["is_scheduled"] = True
            elif status_filter == "pending":
                query["youtube_video_id"] = {"$exists": False}
                query["is_scheduled"] = False
        
        # Déterminer l'ordre de tri
        sort_direction = -1 if sort_order == "desc" else 1
        
        # Récupérer les vidéos
        videos = await videos_collection.find(
            query,
            {"_id": 0}
        ).sort(sort_by, sort_direction).to_list(length=None)
        
        return videos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing videos: {str(e)}"
        )
