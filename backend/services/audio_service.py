import os
from typing import List
from models import AudioGeneration, AudioPhrase
from services.elevenlabs_service import ElevenLabsService
from slugify import slugify

class AudioService:
    """
    Service pour gérer la génération d'audio avec timestamps
    """
    
    def __init__(self):
        self.elevenlabs_service = ElevenLabsService()
        self.resources_dir = os.getenv("RESOURCES_DIR", "/app/ressources")
        self.base_audio_dir = os.path.join(self.resources_dir, "videos")
    
    def _get_audio_directory(self, title: str) -> str:
        """Créer le répertoire audio pour une vidéo"""
        slug = slugify(title)
        video_dir = os.path.join(self.base_audio_dir, slug)
        audio_dir = os.path.join(video_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        return audio_dir
    
    async def generate_audio_with_timestamps(
        self,
        script_id: str,
        idea_id: str,
        phrases: List[str]
    ) -> AudioGeneration:
        """
        Générer l'audio pour chaque phrase avec timestamps
        """
        try:
            # Récupérer le titre pour créer le répertoire
            from database import get_ideas_collection
            ideas_collection = get_ideas_collection()
            idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
            
            if not idea:
                raise ValueError(f"Idea {idea_id} not found")
            
            audio_dir = self._get_audio_directory(idea["title"])
            
            # Générer l'audio pour chaque phrase
            audio_phrases = []
            cumulative_time = 0
            
            for i, phrase_text in enumerate(phrases):
                output_path = os.path.join(audio_dir, f"phrase_{i:03d}.mp3")
                
                # Générer l'audio
                audio_path, duration_ms = await self.elevenlabs_service.generate_audio(
                    text=phrase_text,
                    output_path=output_path
                )
                
                # Créer l'objet AudioPhrase avec timestamps
                audio_phrase = AudioPhrase(
                    phrase_index=i,
                    phrase_text=phrase_text,
                    audio_path=audio_path,
                    duration_ms=duration_ms,
                    start_time_ms=cumulative_time,
                    end_time_ms=cumulative_time + duration_ms
                )
                
                audio_phrases.append(audio_phrase)
                cumulative_time += duration_ms
                
                print(f"✅ Generated audio {i+1}/{len(phrases)}: {phrase_text[:50]}...")
            
            # Créer l'objet AudioGeneration
            audio_generation = AudioGeneration(
                script_id=script_id,
                idea_id=idea_id,
                phrases=audio_phrases,
                total_duration_ms=cumulative_time,
                audio_directory=audio_dir
            )
            
            print(f"✅ Audio generation complete: {len(audio_phrases)} phrases, {cumulative_time/1000:.2f}s total")
            return audio_generation
            
        except Exception as e:
            print(f"❌ Error generating audio: {str(e)}")
            raise
    
    async def generate_audio_complete(self, script_id: str) -> AudioGeneration:
        """
        Générer l'audio pour un script (méthode complète)
        
        Cette méthode:
        1. Récupère le script depuis MongoDB
        2. Génère l'audio avec timestamps
        3. Sauvegarde les phrases audio dans le script
        4. Met à jour le statut de l'idée
        
        Args:
            script_id: ID du script
            
        Returns:
            AudioGeneration: Objet contenant les infos audio
        """
        try:
            from database import get_scripts_collection, get_ideas_collection
            from models import IdeaStatus
            
            # 1. Récupérer le script
            scripts_collection = get_scripts_collection()
            script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
            
            if not script:
                raise ValueError(f"Script {script_id} not found")
            
            # 2. Générer l'audio
            audio_generation = await self.generate_audio_with_timestamps(
                script_id=script_id,
                idea_id=script["idea_id"],
                phrases=script["phrases"]
            )
            
            # 3. Sauvegarder les phrases audio dans le script
            await scripts_collection.update_one(
                {"id": script_id},
                {"$set": {"audio_phrases": [phrase.model_dump() for phrase in audio_generation.phrases]}}
            )
            
            # 4. Mettre à jour le statut de l'idée
            ideas_collection = get_ideas_collection()
            await ideas_collection.update_one(
                {"id": script["idea_id"]},
                {"$set": {"status": IdeaStatus.AUDIO_GENERATED}}
            )
            
            print(f"✅ Audio generation complete for script {script_id}")
            return audio_generation
            
        except Exception as e:
            print(f"❌ Error in generate_audio_complete: {str(e)}")
            raise

