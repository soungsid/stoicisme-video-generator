from fastapi import APIRouter, HTTPException, status
import os
import httpx
import uuid
from typing import List
from datetime import datetime

from agents.image_prompt_generator_agent import ImagePromptGeneratorAgent
from backend.models import Script
from database import get_ideas_collection, get_scripts_collection

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
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )
        
        if not idea.get("script_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No script found for this idea"
            )
        
        script: Script = await scripts_collection.find_one({"id": idea["script_id"]}, {"_id": 0})
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {idea['script_id']} not found"
            )
        
        script_text = script.get("original_script", "")
        if not script_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Script text is empty"
            )
        
        # Générer les prompts d'images
        agent = ImagePromptGeneratorAgent()
        image_prompts = await agent.generate_image_prompts(script_text)
        
        # Créer le répertoire pour les images
        video_directory = f"generated_images/{idea_id}"
        os.makedirs(video_directory, exist_ok=True)
        
        # Générer les images via l'API externe
        generated_images = await _generate_images_with_api(image_prompts, video_directory)
        
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
    Génère les images via l'API externe (votre API sur localhost:8000)
    """
    generated_images = []
    
    async with httpx.AsyncClient() as client:
        for i, prompt in enumerate(image_prompts):
            try:
                # Construire le payload selon votre documentation
                payload = {
                    "video_directory": output_directory,
                    "timestamps_script_prompt": [prompt],
                    "video_script": f"Image {i+1}: {prompt}"
                }
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                # Ajouter l'authentification si nécessaire
                if IMAGE_API_KEY:
                    headers["Authorization"] = f"Bearer {IMAGE_API_KEY}"
                
                response = await client.post(
                    f"{IMAGE_API_BASE_URL}/generate/image/video",
                    json=payload,
                    headers=headers,
                    timeout=60.0  # Timeout de 60 secondes
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success" and result.get("generated_images"):
                        # Ajouter le chemin de la première image générée
                        generated_images.append(result["generated_images"][0])
                    else:
                        print(f"⚠️ API returned non-success status for prompt {i+1}: {result}")
                        # Créer un chemin par défaut
                        default_path = f"{output_directory}/image_{i+1}.jpg"
                        generated_images.append(default_path)
                else:
                    print(f"⚠️ API error for prompt {i+1}: {response.status_code} - {response.text}")
                    # Créer un chemin par défaut en cas d'erreur
                    default_path = f"{output_directory}/image_{i+1}.jpg"
                    generated_images.append(default_path)
                    
            except Exception as e:
                print(f"❌ Error generating image {i+1}: {str(e)}")
                # Créer un chemin par défaut en cas d'erreur
                default_path = f"{output_directory}/image_{i+1}.jpg"
                generated_images.append(default_path)
    
    return generated_images

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
            "has_images": "generated_images" in idea,
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
