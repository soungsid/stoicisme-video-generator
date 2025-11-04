from fastapi import APIRouter, HTTPException, status
from models import AudioGeneration, IdeaStatus
from database import get_scripts_collection, get_ideas_collection
from services.audio_service import AudioService
from datetime import datetime
import os

router = APIRouter()

@router.post("/generate/{script_id}", response_model=AudioGeneration)
async def generate_audio(script_id: str):
    """
    Générer l'audio pour un script adapté avec timestamps
    """
    try:
        scripts_collection = get_scripts_collection()
        script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
        
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {script_id} not found"
            )
        
        if not script.get("elevenlabs_adapted_script") or not script.get("phrases"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Script must be adapted for ElevenLabs before audio generation"
            )
        
        # Générer l'audio
        audio_service = AudioService()
        audio_generation = await audio_service.generate_audio_with_timestamps(
            script_id=script_id,
            idea_id=script["idea_id"],
            phrases=script["phrases"]
        )
        
        # Sauvegarder les phrases audio dans le script
        await scripts_collection.update_one(
            {"id": script_id},
            {"$set": {"audio_phrases": [phrase.model_dump() for phrase in audio_generation.phrases]}}
        )
        
        # Mettre à jour le statut de l'idée
        ideas_collection = get_ideas_collection()
        await ideas_collection.update_one(
            {"id": script["idea_id"]},
            {"$set": {"status": IdeaStatus.AUDIO_GENERATED}}
        )
        
        return audio_generation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating audio: {str(e)}"
        )

@router.get("/by-script/{script_id}")
async def get_audio_by_script(script_id: str):
    """
    Récupérer les informations audio pour un script
    """
    try:
        # Chercher dans le répertoire audio
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
        
        # Vérifier si l'audio existe
        from services.video_service import VideoService
        video_service = VideoService()
        audio_dir = video_service.get_video_directory(idea["title"], "audio")
        
        if not os.path.exists(audio_dir):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio not generated yet"
            )
        
        audio_files = [f for f in os.listdir(audio_dir) if f.endswith(".mp3")]
        
        return {
            "script_id": script_id,
            "idea_id": idea_id,
            "audio_directory": audio_dir,
            "audio_files": audio_files,
            "total_files": len(audio_files)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching audio: {str(e)}"
        )
