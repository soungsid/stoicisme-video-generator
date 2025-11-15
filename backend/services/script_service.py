from fastapi import HTTPException, status
from database import get_scripts_collection, get_ideas_collection
from models import Script, ScriptGenerationRequest, IdeaStatus
from agents.script_generator_agent import ScriptGeneratorAgent
from agents.script_adapter_agent import ScriptAdapterAgent
from agents.youtube_description_agent import YouTubeDescriptionAgent
from agents.long_video_script_agent import LongVideoScriptAgent
from services.conclusion_script_service import ConclusionScriptService

class ScriptService:

 
    # ----------------------------------------------------------------------
    # Génération de script
    # ----------------------------------------------------------------------
    async def generate_script(self, idea_id) -> Script:

        idea = await get_ideas_collection().find_one({"id": idea_id}, {"_id": 0})
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Idea {idea_id} not found"
            )

        

        video_type = idea.get("video_type", "short")
        sections_count = idea.get("sections_count")
        titles   = idea.get("section_titles", [])

        # VIDEO LONGUE AVEC SECTIONS
        is_long = (video_type == "normal" and sections_count and sections_count > 0 and len(titles) > 0)

        if is_long:
            print(f"🎬 Génération d'un script LONG avec {sections_count} sections")

            agent = LongVideoScriptAgent()
            conclusion_service = ConclusionScriptService()

            script_text, sec = await agent.generate_full_script_with_sections(
                title=idea["title"],
                keywords=idea.get("keywords", []),
                section_titles=titles,
                total_duration_seconds=idea.duration_seconds
            )

            conclusion = await conclusion_service._generate_simple_conclusion(
                title=idea["title"],
                keywords=idea.get("keywords", [])
            )

            script_text += conclusion

            script = Script(
                idea_id=idea_id,
                title=idea["title"],
                original_script=script_text
            )

        # SCRIPT CLASSIQUE
        else:
            agent = ScriptGeneratorAgent()
            script = await agent.generate_script(
                title=idea["title"],
                keywords=idea.get("keywords", []),
                duration_seconds=idea.duration_seconds
            )

        # Description YouTube
        try:
            desc_agent = YouTubeDescriptionAgent()
            description = await desc_agent.generate_description(
                title=idea["title"],
                script_content=script.original_script,
                keywords=idea.get("keywords", [])
            )
            print(f"description pondu par description agent : {description}")
            script.youtube_description = description

        except Exception:
            print(f"Erreur lors de la generation de la description youtube")

            script.youtube_description = idea["title"]

        # Sauvegarde en DB
        await get_scripts_collection().insert_one(script.model_dump())

        # Update statut
        await get_ideas_collection().update_one(
            {"id": idea_id},
            {"$set": {"status": IdeaStatus.SCRIPT_GENERATED}}
        )

        return script

    # ----------------------------------------------------------------------
    # Adaptation ElevenLabs
    # ----------------------------------------------------------------------
    async def adapt_script(self, script_id: str):
        script = await get_scripts_collection().find_one({"id": script_id}, {"_id": 0})

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

        adapter = ScriptAdapterAgent()
        adapted_script, phrases = await adapter.adapt_script(
            original_script=script["original_script"]
        )

        updated = await get_scripts_collection().find_one_and_update(
            {"id": script_id},
            {"$set": {
                "elevenlabs_adapted_script": adapted_script,
                "phrases": phrases
            }},
            return_document=True,
            projection={"_id": 0}
        )

        return updated

    # ----------------------------------------------------------------------
    # Get script
    # ----------------------------------------------------------------------
    async def get_script(self, script_id: str):
        script = await get_scripts_collection().find_one({"id": script_id}, {"_id": 0})
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {script_id} not found"
            )
        return script

    # ----------------------------------------------------------------------
    # Get script by idea
    # ----------------------------------------------------------------------
    async def get_script_by_idea(self, idea_id: str):
        script = await get_scripts_collection().find_one({"idea_id": idea_id}, {"_id": 0})
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script for idea {idea_id} not found"
            )
        return script

    # ----------------------------------------------------------------------
    # Update script
    # ----------------------------------------------------------------------
    async def update_script(self, script_id: str, title=None, original_script=None, keywords=None):

        script = await get_scripts_collection().find_one({"id": script_id}, {"_id": 0})
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script {script_id} not found"
            )

        update_data = {}

        if title:
            update_data["title"] = title
            await get_ideas_collection().update_one(
                {"id": script["idea_id"]},
                {"$set": {"title": title}}
            )

        if original_script:
            update_data["original_script"] = original_script
            update_data["elevenlabs_adapted_script"] = None
            update_data["phrases"] = []

        if keywords:
            await get_ideas_collection().update_one(
                {"id": script["idea_id"]},
                {"$set": {"keywords": keywords}}
            )

        if update_data:
            updated = await get_scripts_collection().find_one_and_update(
                {"id": script_id},
                {"$set": update_data},
                return_document=True,
                projection={"_id": 0}
            )
            return updated
        
        return script
