from fastapi import APIRouter, HTTPException, status
from models import IdeaStatus
from database import get_ideas_collection, get_scripts_collection
from services.queue_service import QueueService
import traceback

router = APIRouter()

async def update_idea_progress(idea_id: str, status_value: IdeaStatus, progress: int, step: str, error: str = None):
    """Mettre à jour la progression d'une idée"""
    ideas_collection = get_ideas_collection()
    update_data = {
        "status": status_value,
        "progress_percentage": progress,
        "current_step": step
    }
    if error:
        update_data["error_message"] = error
    
    await ideas_collection.update_one(
        {"id": idea_id},
        {"$set": update_data}
    )

async def run_pipeline(idea_id: str, start_from: str = "script"):
    """Exécuter le pipeline complet de génération"""
    try:
        ideas_collection = get_ideas_collection()
        scripts_collection = get_scripts_collection()
        
        # Récupérer l'idée
        idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
        if not idea:
            return
        
        script_id = None
        
        # Étape 1: Générer le script
        if start_from == "script":
            await update_idea_progress(idea_id, IdeaStatus.SCRIPT_GENERATING, 10, "Génération du script...")
            
            agent = ScriptGeneratorAgent()
            script = await agent.generate_script(
                title=idea["title"],
                keywords=idea.get("keywords", []),
                duration_seconds=idea["duration_seconds"]
            )
            script.idea_id = idea_id
            script.title = idea["title"]
            
            await scripts_collection.insert_one(script.model_dump())
            script_id = script.id
            
            await update_idea_progress(idea_id, IdeaStatus.SCRIPT_GENERATED, 25, "Script généré")
        else:
            # Récupérer le script existant
            script = await scripts_collection.find_one({"idea_id": idea_id}, {"_id": 0})
            if script:
                script_id = script["id"]
        
        # Étape 2: Adapter le script
        if start_from in ["script", "adapt"] and script_id:
            await update_idea_progress(idea_id, IdeaStatus.SCRIPT_ADAPTING, 35, "Adaptation ElevenLabs...")
            
            adapter = ScriptAdapterAgent()
            script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
            adapted_script, phrases = await adapter.adapt_script(script["original_script"])
            
            await scripts_collection.update_one(
                {"id": script_id},
                {"$set": {
                    "elevenlabs_adapted_script": adapted_script,
                    "phrases": phrases
                }}
            )
            
            await update_idea_progress(idea_id, IdeaStatus.SCRIPT_ADAPTED, 50, "Script adapté")
        
        # Étape 3: Générer l'audio
        if start_from in ["script", "adapt", "audio"] and script_id:
            await update_idea_progress(idea_id, IdeaStatus.AUDIO_GENERATING, 60, "Génération audio...")
            
            script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
            audio_service = AudioService()
            audio_generation = await audio_service.generate_audio_with_timestamps(
                script_id=script_id,
                idea_id=idea_id,
                phrases=script["phrases"]
            )
            
            # Sauvegarder les timestamps
            await scripts_collection.update_one(
                {"id": script_id},
                {"$set": {"audio_phrases": [phrase.model_dump() for phrase in audio_generation.phrases]}}
            )
            
            await update_idea_progress(idea_id, IdeaStatus.AUDIO_GENERATED, 75, "Audio généré")
        
        # Étape 4: Générer la vidéo
        if start_from in ["script", "adapt", "audio", "video"] and script_id:
            await update_idea_progress(idea_id, IdeaStatus.VIDEO_GENERATING, 85, "Génération vidéo...")
            
            script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
            video_service = VideoService()
            video = await video_service.generate_video(idea=idea, script=script)
            
            from database import get_videos_collection
            videos_collection = get_videos_collection()
            await videos_collection.insert_one(video.model_dump())
            
            await update_idea_progress(idea_id, IdeaStatus.VIDEO_GENERATED, 100, "Vidéo prête !")
        
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ Pipeline error for {idea_id}: {error_msg}")
        await update_idea_progress(idea_id, IdeaStatus.ERROR, 0, "Erreur", error_msg[:500])

@router.post("/generate/{idea_id}")
async def start_pipeline(idea_id: str, background_tasks: BackgroundTasks, start_from: str = "script"):
    """
    Démarrer le pipeline de génération
    start_from: 'script', 'adapt', 'audio', 'video'
    """
    try:
        ideas_collection = get_ideas_collection()
        idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
        
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        if idea["status"] == IdeaStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Idea must be validated first"
            )
        
        # Lancer le pipeline en background
        background_tasks.add_task(run_pipeline, idea_id, start_from)
        
        return {
            "success": True,
            "message": "Pipeline started",
            "idea_id": idea_id,
            "start_from": start_from
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting pipeline: {str(e)}"
        )

@router.get("/status/{idea_id}")
async def get_pipeline_status(idea_id: str):
    """Obtenir le statut du pipeline"""
    try:
        ideas_collection = get_ideas_collection()
        idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
        
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        return {
            "idea_id": idea_id,
            "status": idea["status"],
            "progress_percentage": idea.get("progress_percentage", 0),
            "current_step": idea.get("current_step"),
            "error_message": idea.get("error_message")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting status: {str(e)}"
        )
