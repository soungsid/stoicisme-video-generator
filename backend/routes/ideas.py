from fastapi import APIRouter, HTTPException, status
from typing import List
from models import VideoIdea, IdeaStatus, IdeaGenerationRequest, ValidateIdeaRequest, Script
from database import get_ideas_collection
from services.idea_management_service import IdeaManagementService
from datetime import datetime

router = APIRouter()

@router.post("/generate", response_model=dict)
async def generate_ideas(request: IdeaGenerationRequest):
    """
    Générer de nouvelles idées de vidéos sur le stoïcisme
    
    Modes disponibles :
    - Génération automatique (count idées)
    - Génération avec mots-clés
    - Titre personnalisé (une seule idée)
    - Script personnalisé (une seule idée, script_text fourni)
    
    Si script_text est fourni, le script ne sera pas généré automatiquement.
    """
    try:
        service = IdeaManagementService()
        result = await service.create_ideas(request)
        return result
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


@router.delete("/{idea_id}")
async def delete_idea(idea_id: str):
    """
    Supprimer une idée
    """
    try:
        from services.idea_service import IdeaService
        
        service = IdeaService()
        result = await service.delete_idea(idea_id=idea_id)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting idea: {str(e)}"
        )

@router.post("/batch-action")
async def batch_action(idea_ids: List[str], action: str):
    """
    Effectuer une action sur plusieurs idées à la fois
    Actions possibles: delete, generate
    """
    try:
        from services.queue_service import QueueService
        
        ideas_collection = get_ideas_collection()
        results = {
            "success": [],
            "failed": [],
            "total": len(idea_ids)
        }
        
        for idea_id in idea_ids:
            try:
                idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
                
                if not idea:
                    results["failed"].append({
                        "id": idea_id,
                        "reason": "Idea not found"
                    })
                    continue
                
                if action == "delete":
                    # Supprimer l'idée
                    from services.idea_service import IdeaService
                    idea_service = IdeaService()
                    await idea_service.delete_idea(idea_id)
                    results["success"].append(idea_id)
                    
                elif action == "generate":
                    # Ajouter à la queue de génération
                    if idea["status"] != IdeaStatus.PENDING:
                        results["failed"].append({
                            "id": idea_id,
                            "reason": "Idea is not pending"
                        })
                        continue
                    
                    queue_service = QueueService()
                    await queue_service.add_job(idea_id, start_from="script")
                    results["success"].append(idea_id)
                    
                else:
                    results["failed"].append({
                        "id": idea_id,
                        "reason": f"Unknown action: {action}"
                    })
                    
            except Exception as e:
                results["failed"].append({
                    "id": idea_id,
                    "reason": str(e)
                })
        
        return {
            "success": True,
            "message": f"Batch action '{action}' completed",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing batch action: {str(e)}"
        )

@router.post("/{idea_id}/generate-section-titles")
async def generate_section_titles(idea_id: str, sections_count: int):
    """
    Générer ou régénérer les titres de sections pour une idée
    """
    try:
        ideas_collection = get_ideas_collection()
        idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
        
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        from agents.section_title_generator_agent import SectionTitleGeneratorAgent
        agent = SectionTitleGeneratorAgent()
        
        section_titles = await agent.generate_section_titles(
            title=idea["title"],
            keywords=idea.get("keywords", []),
            sections_count=sections_count
        )
        
        # Mettre à jour l'idée
        await ideas_collection.update_one(
            {"id": idea_id},
            {
                "$set": {
                    "section_titles": section_titles,
                    "sections_count": sections_count
                }
            }
        )
        
        return {
            "success": True,
            "idea_id": idea_id,
            "section_titles": section_titles,
            "sections_count": sections_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating section titles: {str(e)}"
        )
