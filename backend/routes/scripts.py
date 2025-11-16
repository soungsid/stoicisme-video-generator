from fastapi import APIRouter
from models import ScriptGenerationRequest
from services.script_service import ScriptService


router = APIRouter()
service = ScriptService()

@router.post("/generate")
async def generate_script(request: ScriptGenerationRequest):
    return await service.generate_script(request.idea_id)

@router.post("/{script_id}/adapt")
async def adapt_script(script_id: str):
    return await service.adapt_script(script_id)

@router.get("/{script_id}")
async def get_script(script_id: str):
    return await service.get_script(script_id)

@router.get("/by-idea/{idea_id}")
async def get_script_by_idea(idea_id: str):
    return await service.get_script_by_idea(idea_id)

@router.patch("/{script_id}")
async def update_script(script_id: str, title=None, original_script=None, keywords=None, youtube_description=None, video_guideline=None):
    return await service.update_script(script_id, title, original_script, keywords, youtube_description, video_guideline)
