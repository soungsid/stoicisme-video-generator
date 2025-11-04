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
        self.base_audio_dir = "../ressources/videos"
    
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
