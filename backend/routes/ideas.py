from fastapi import APIRouter, HTTPException, status
from typing import List
from models import VideoIdea, IdeaStatus, IdeaGenerationRequest, ValidateIdeaRequest
from database import get_ideas_collection
from agents.idea_generator_agent import IdeaGeneratorAgent
from datetime import datetime

router = APIRouter()

@router.post("/generate", response_model=dict)
async def generate_ideas(request: IdeaGenerationRequest):
    """
    Générer de nouvelles idées de vidéos sur le stoïcisme
    """
    try:
        agent = IdeaGeneratorAgent()
        ideas = await agent.generate_ideas(count=request.count)
        
        # Sauvegarder en base de données
        ideas_collection = get_ideas_collection()
        ideas_dict = [idea.model_dump() for idea in ideas]
        
        if ideas_dict:
            await ideas_collection.insert_many(ideas_dict)
        
        return {
            "success": True,
            "count": len(ideas),
            "ideas": ideas_dict
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating ideas: {str(e)}"
        )

@router.get("/", response_model=List[VideoIdea])
async def get_all_ideas():
    """
    Récupérer toutes les idées de vidéos
    """
    try:
        ideas_collection = get_ideas_collection()
        ideas = await ideas_collection.find({}, {"_id": 0}).sort("created_at", -1).to_list(length=None)
        return ideas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ideas: {str(e)}"
        )

@router.get("/{idea_id}", response_model=VideoIdea)
async def get_idea(idea_id: str):
    """
    Récupérer une idée spécifique
    """
    try:
        ideas_collection = get_ideas_collection()
        idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
        
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        return idea
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching idea: {str(e)}"
        )

@router.patch("/{idea_id}/validate", response_model=VideoIdea)
async def validate_idea(idea_id: str, request: ValidateIdeaRequest):
    """
    Valider une idée et définir ses paramètres (durée, type)
    """
    try:
        ideas_collection = get_ideas_collection()
        
        update_data = {
            "status": IdeaStatus.VALIDATED,
            "validated_at": datetime.now(),
            "video_type": request.video_type,
            "duration_seconds": request.duration_seconds
        }
        
        if request.keywords:
            update_data["keywords"] = request.keywords
        
        result = await ideas_collection.find_one_and_update(
            {"id": idea_id},
            {"$set": update_data},
            return_document=True,
            projection={"_id": 0}
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating idea: {str(e)}"
        )

@router.patch("/{idea_id}/reject", response_model=VideoIdea)
async def reject_idea(idea_id: str):
    """
    Rejeter une idée
    """
    try:
        ideas_collection = get_ideas_collection()
        
        result = await ideas_collection.find_one_and_update(
            {"id": idea_id},
            {"$set": {"status": IdeaStatus.REJECTED}},
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rejecting idea: {str(e)}"
        )

@router.delete("/{idea_id}")
async def delete_idea(idea_id: str):
    """
    Supprimer une idée
    """
    try:
        ideas_collection = get_ideas_collection()
        result = await ideas_collection.delete_one({"id": idea_id})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        return {"success": True, "message": "Idea deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting idea: {str(e)}"
        )
