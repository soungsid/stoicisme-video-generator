from fastapi import APIRouter, HTTPException, status
from models import Script, ScriptGenerationRequest, IdeaStatus
from database import get_scripts_collection, get_ideas_collection
from agents.script_generator_agent import ScriptGeneratorAgent
from agents.script_adapter_agent import ScriptAdapterAgent
from datetime import datetime

router = APIRouter()

@router.post("/generate", response_model=Script)
async def generate_script(request: ScriptGenerationRequest):
    """
    Générer un script à partir d'une idée validée
    """
    try:
        # Vérifier que l'idée existe et est validée
        ideas_collection = get_ideas_collection()
        idea = await ideas_collection.find_one({"id": request.idea_id}, {"_id": 0})
        
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {request.idea_id} not found"
            )
        
        if idea["status"] != IdeaStatus.VALIDATED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Idea must be validated before generating script"
            )
        
        # Générer le script
        agent = ScriptGeneratorAgent()
        script = await agent.generate_script(
            title=idea["title"],
            keywords=idea.get("keywords", []),
            duration_seconds=request.duration_seconds
        )
        script.idea_id = request.idea_id
        script.title = idea["title"]
        
        # Sauvegarder le script
        scripts_collection = get_scripts_collection()
        await scripts_collection.insert_one(script.model_dump())
        
        # Mettre à jour le statut de l'idée
        await ideas_collection.update_one(
            {"id": request.idea_id},
            {"$set": {"status": IdeaStatus.SCRIPT_GENERATED}}
        )
        
        return script
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating script: {str(e)}"
        )

@router.post("/{script_id}/adapt", response_model=Script)
async def adapt_script_for_elevenlabs(script_id: str):
    """
    Adapter le script pour ElevenLabs V3 avec marqueurs d'émotion
    """
    try:
        scripts_collection = get_scripts_collection()
        script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
        
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {script_id} not found"
            )
        
        if not script.get("original_script"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Script has no original content to adapt"
            )
        
        # Adapter le script
        adapter = ScriptAdapterAgent()
        adapted_script, phrases = await adapter.adapt_script(
            original_script=script["original_script"]
        )
        
        # Mettre à jour le script
        result = await scripts_collection.find_one_and_update(
            {"id": script_id},
            {
                "$set": {
                    "elevenlabs_adapted_script": adapted_script,
                    "phrases": phrases
                }
            },
            return_document=True,
            projection={"_id": 0}
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adapting script: {str(e)}"
        )

@router.get("/{script_id}", response_model=Script)
async def get_script(script_id: str):
    """
    Récupérer un script spécifique
    """
    try:
        scripts_collection = get_scripts_collection()
        script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
        
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {script_id} not found"
            )
        
        return script
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching script: {str(e)}"
        )

@router.get("/by-idea/{idea_id}", response_model=Script)
async def get_script_by_idea(idea_id: str):
    """
    Récupérer le script d'une idée
    """
    try:
        scripts_collection = get_scripts_collection()
        script = await scripts_collection.find_one({"idea_id": idea_id}, {"_id": 0})
        
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script for idea {idea_id} not found"
            )
        
        return script
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching script: {str(e)}"
        )
