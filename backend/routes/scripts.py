from fastapi import APIRouter, HTTPException, status
from models import Script, ScriptGenerationRequest, IdeaStatus
from typing import List
from database import get_scripts_collection, get_ideas_collection
from agents.script_generator_agent import ScriptGeneratorAgent
from agents.script_adapter_agent import ScriptAdapterAgent
from datetime import datetime

router = APIRouter()

@router.post("/generate", response_model=Script)
async def generate_script(request: ScriptGenerationRequest):
    """
    Générer un script à partir d'une idée validée
    
    - Pour vidéos SHORT: Génère un script classique
    - Pour vidéos NORMAL avec sections: Génère un script avec sections séquentielles + conclusion intelligente
    
    Génère également automatiquement la description YouTube
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
        
        video_type = idea.get("video_type", "short")
        sections_count = idea.get("sections_count")
        section_titles = idea.get("section_titles", [])
        
        # Vérifier si c'est une vidéo longue avec sections
        is_long_video = (video_type == "normal" and sections_count and 
                        sections_count > 0 and len(section_titles) > 0)
        
        if is_long_video:
            # Générer un script long avec sections
            print(f"🎬 Génération d'un script LONG avec {sections_count} sections")
            
            from agents.long_video_script_agent import LongVideoScriptAgent
            from services.conclusion_script_service import ConclusionScriptService
            
            long_agent = LongVideoScriptAgent()
            conclusion_service = ConclusionScriptService()
            
            # Générer introduction + sections
            script_text, sections = await long_agent.generate_full_script_with_sections(
                title=idea["title"],
                keywords=idea.get("keywords", []),
                section_titles=section_titles,
                total_duration_seconds=request.duration_seconds
            )
            
            # Ajouter la conclusion avec recommandation de vidéo
            # Note: On ne peut pas utiliser l'ID de la vidéo car elle n'existe pas encore
            # On générera la conclusion sans recommandation pour le moment
            conclusion = await conclusion_service._generate_simple_conclusion(
                title=idea["title"],
                keywords=idea.get("keywords", [])
            )
            
            script_text += "\n\n=== CONCLUSION ===\n" + conclusion
            
            script = Script(
                idea_id=request.idea_id,
                title=idea["title"],
                original_script=script_text
            )
            
        else:
            # Générer un script classique (short ou normal sans sections)
            print(f"📝 Génération d'un script CLASSIQUE")
            
            agent = ScriptGeneratorAgent()
            script = await agent.generate_script(
                title=idea["title"],
                keywords=idea.get("keywords", []),
                duration_seconds=request.duration_seconds
            )
        
        script.idea_id = request.idea_id
        script.title = idea["title"]
        
        # Générer la description YouTube automatiquement
        try:
            from agents.youtube_description_agent import YouTubeDescriptionAgent
            description_agent = YouTubeDescriptionAgent()
            youtube_description = await description_agent.generate_description(
                title=idea["title"],
                script_content=script.original_script,
                keywords=idea.get("keywords", [])
            )
            script.youtube_description = youtube_description
            print(f"✅ Description YouTube générée: {len(youtube_description)} caractères")
        except Exception as desc_error:
            print(f"⚠️  Erreur lors de la génération de la description YouTube: {desc_error}")
            script.youtube_description = f"{idea['title']}\n\n" + "\n".join([f"#{kw}" for kw in idea.get("keywords", [])])
        
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
        import traceback
        traceback.print_exc()
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

@router.patch("/{script_id}", response_model=Script)
async def update_script(script_id: str, title: str = None, original_script: str = None, keywords: List[str] = None):
    """
    Mettre à jour un script (titre, contenu, mots-clés)
    """
    try:
        scripts_collection = get_scripts_collection()
        ideas_collection = get_ideas_collection()
        
        script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {script_id} not found"
            )
        
        update_data = {}
        
        if title is not None:
            update_data["title"] = title
            # Mettre à jour le titre de l'idée aussi
            await ideas_collection.update_one(
                {"id": script["idea_id"]},
                {"$set": {"title": title}}
            )
        
        if original_script is not None:
            update_data["original_script"] = original_script
            # Réinitialiser le script adapté car le contenu a changé
            update_data["elevenlabs_adapted_script"] = None
            update_data["phrases"] = []
            update_data["audio_phrases"] = None
        
        if keywords is not None:
            # Mettre à jour les mots-clés de l'idée
            await ideas_collection.update_one(
                {"id": script["idea_id"]},
                {"$set": {"keywords": keywords}}
            )
        
        if update_data:
            result = await scripts_collection.find_one_and_update(
                {"id": script_id},
                {"$set": update_data},
                return_document=True,
                projection={"_id": 0}
            )
            return result
        else:
            return script
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating script: {str(e)}"
        )
