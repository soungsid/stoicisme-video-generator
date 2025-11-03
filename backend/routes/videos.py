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
    """
    try:
        scripts_collection = get_scripts_collection()
        script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
        
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {script_id} not found"
            )
        
        idea_id = script["idea_id"]
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
        
        # Générer la vidéo
        video_service = VideoService()
        video = await video_service.generate_video(
            idea=idea,
            script=script
        )
        
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

@router.get("/{video_id}", response_model=Video)
async def get_video(video_id: str):
    """
    Récupérer une vidéo spécifique
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
async def list_videos():
    """
    Lister toutes les vidéos générées
    """
    try:
        videos_collection = get_videos_collection()
        videos = await videos_collection.find({}, {"_id": 0}).sort("created_at", -1).to_list(length=None)
        return videos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing videos: {str(e)}"
        )
