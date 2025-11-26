from fastapi import APIRouter, HTTPException, status
import os
import httpx
import uuid
from typing import List
from datetime import datetime

from agents.image_prompt_generator_agent import ImagePromptGeneratorAgent
from models import Script
from database import get_ideas_collection, get_scripts_collection
from services.resource_config_service import ResourceConfigService

router = APIRouter()

# Configuration de l'API externe pour génération d'images
IMAGE_API_BASE_URL = os.getenv("IMAGE_API_BASE_URL", "http://localhost:8000")
IMAGE_API_KEY = os.getenv("IMAGE_API_KEY", "")

class VideoImagesRequest:
    def __init__(self, video_directory: str, timestamps_script_prompt: List[str], video_script: str):
        self.video_directory = video_directory
        self.timestamps_script_prompt = timestamps_script_prompt
        self.video_script = video_script

class VideoImagesResponse:
    def __init__(self, generated_images: List[str], video_directory: str, total_images: int, status: str):
        self.generated_images = generated_images
        self.video_directory = video_directory
        self.total_images = total_images
        self.status = status

@router.post("/generate/{idea_id}")
async def generate_images_for_idea(idea_id: str):
    """
    Génère des images pour une idée en utilisant le script existant
    """
    try:
        # Récupérer l'idée et le script
        ideas_collection = get_ideas_collection()
        scripts_collection = get_scripts_collection()
        
        idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})        
        script: Script = await scripts_collection.find_one({"id": idea["script_id"]}, {"_id": 0})
        script_text = script.get("original_script", "")
       
        # Générer les prompts d'images
        agent = ImagePromptGeneratorAgent()
        image_prompts = await agent.generate_image_prompts(script_text)
        
        # Utiliser ResourceConfigService pour obtenir le répertoire des images
        resource_config = ResourceConfigService()
        directories = resource_config.get_idea_directories(idea_id, idea.get("title", ""))
        image_directory = directories["image_directory"]
        
        # Générer les images via l'API externe
        generated_images = await _generate_images_with_api(image_prompts, image_directory)
        
        # Mettre à jour l'idée avec les informations d'images
        await ideas_collection.update_one(
            {"id": idea_id},
            {
                "$set": {
                    "image_prompts": image_prompts,
                    "generated_images": generated_images,
                    "total_images": len(generated_images),
                    "images_generated_at": datetime.now().isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "message": f"Generated {len(generated_images)} images successfully",
            "idea_id": idea_id,
            "generated_images": generated_images,
            "total_images": len(generated_images),
            "image_prompts": image_prompts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating images: {str(e)}"
        )

async def _generate_images_with_api(image_prompts: List[str], output_directory: str) -> List[str]:
    """
    Génère toutes les images en une seule requête via l'API externe
    """
    # Construire le payload avec tous les prompts
    payload = {
        "video_directory": output_directory,
        "timestamps_script_prompt": [image_prompts[0]],
        "video_script": f"Video script with {len(image_prompts)} images"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        print(f"📞 call the {IMAGE_API_BASE_URL}/generate/image/video")
        response = await client.post(
            f"{IMAGE_API_BASE_URL}/generate/image/video",
            json=payload,
            headers=headers,
            timeout=300.0  # Timeout de 5 minutes pour générer toutes les images
        )
        result = response.json()
        return result["generated_images"]
                
    

@router.get("/status/{idea_id}")
async def get_images_status(idea_id: str):
    """
    Récupère le statut des images générées pour une idée
    """
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
            "total_images": idea.get("total_images", 0),
            "generated_images": idea.get("generated_images", []),
            "image_prompts": idea.get("image_prompts", []),
            "images_generated_at": idea.get("images_generated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting images status: {str(e)}"
        )
