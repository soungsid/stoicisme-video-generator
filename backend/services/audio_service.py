import os
from typing import List
from models import AudioGeneration, AudioPhrase, Timestamp, TimestampItem
from services.elevenlabs_custom_service import ElevenLabsService
from services.resource_config_service import ResourceConfigService
from slugify import slugify
from pydub import AudioSegment

class AudioService:
    """
    Service pour gérer la génération d'audio avec timestamps
    """
    
    def __init__(self):
        self.elevenlabs_service = ElevenLabsService()
        self.resource_config = ResourceConfigService()
    
    def _get_audio_directory(self, idea_id: str, title: str) -> str:
        """Créer le répertoire audio pour une idée"""
        directories = self.resource_config.get_idea_directories(idea_id, title)
        return directories["audio_directory"]
    
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
            
            audio_dir = self._get_audio_directory(idea_id, idea["title"])
            
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
    
    def _concatenate_audio_files(self, audio_dir: str, output_path: str) -> int:
        """Concaténer tous les fichiers audio dans un seul fichier"""
        audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])
        
        if not audio_files:
            raise ValueError("No audio files found")
        
        # Utiliser pydub pour concaténer
        combined = AudioSegment.empty()
        for audio_file in audio_files:
            audio_path = os.path.join(audio_dir, audio_file)
            audio = AudioSegment.from_mp3(audio_path)
            combined += audio
        
        # Exporter
        combined.export(output_path, format="mp3")
        duration_ms = len(combined)
        
        print(f"✅ Concatenated {len(audio_files)} audio files: {duration_ms/1000:.2f}s")
        return duration_ms
    
    async def generate_timestamps_with_assemblyai(self, audio_path: str, idea_id: str) -> Timestamp:
        """
        Générer les timestamps à partir de l'audio avec AssemblyAI
        Retourne un seul document Timestamp contenant tous les timestamps de l'idée
        """
        try:
            print(f"🎯 Generating timestamps with AssemblyAI for idea {idea_id}")
            
            # Utiliser le service AssemblyAI pour transcrire et obtenir directement l'objet Timestamp
            from services.assemblyai_service import AssemblyAIService
            assemblyai_service = AssemblyAIService()
            
            timestamp_document = await assemblyai_service.transcribe_and_get_timestamps(audio_path, idea_id)
            
            if not timestamp_document:
                raise ValueError("AssemblyAI transcription failed")
            
            print(f"✅ Generated {len(timestamp_document.timestamps)} timestamps for idea {idea_id} in a single document")
            return timestamp_document
            
        except Exception as e:
            print(f"❌ Error generating timestamps with AssemblyAI: {str(e)}")
            raise
    
    async def generate_timestamps_only(self, idea_id: str) -> Timestamp:
        """
        Générer uniquement les timestamps pour une idée (si l'audio existe déjà)
        """
        try:
            from database import get_ideas_collection, get_timestamps_collection
            
            # Vérifier si les timestamps existent déjà
            timestamps_collection = get_timestamps_collection()
            existing_timestamp = await timestamps_collection.find_one({"idea_id": idea_id}, {"_id": 0})
            
            if existing_timestamp:
                print(f"✅ Timestamps already exist for idea {idea_id}, skipping generation")
                return Timestamp(**existing_timestamp)
            
            # Récupérer l'idée pour obtenir le titre
            ideas_collection = get_ideas_collection()
            idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
            
            if not idea:
                raise ValueError(f"Idea {idea_id} not found")
            
            # Vérifier si l'audio concaténé existe
            audio_dir = self._get_audio_directory(idea_id, idea["title"])
            combined_audio_path = os.path.join(audio_dir, "combined_audio.mp3")
            
            if not os.path.exists(combined_audio_path):
                raise ValueError(f"Combined audio file not found for idea {idea_id}: {combined_audio_path}")
            
            # Générer les timestamps
            timestamp_document = await self.generate_timestamps_with_assemblyai(combined_audio_path, idea_id)
            
            # Sauvegarder les timestamps
            await timestamps_collection.insert_one(timestamp_document.model_dump())
            
            print(f"✅ Generated {len(timestamp_document.timestamps)} timestamps for idea {idea_id}")
            return timestamp_document
            
        except Exception as e:
            print(f"❌ Error generating timestamps only: {str(e)}")
            raise
    
    async def complete_audio_generation_with_timestamps(self, script_id: str) -> AudioGeneration:
        """
        Générer l'audio complet avec concaténation et timestamps
        """
        try:
            from database import get_scripts_collection, get_ideas_collection, get_timestamps_collection
            from models import IdeaStatus
            
            # 1. Récupérer le script
            scripts_collection = get_scripts_collection()
            script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
            
            if not script:
                raise ValueError(f"Script {script_id} not found")
            
            idea_id = script["idea_id"]
            
            # 2. Générer l'audio avec timestamps
            audio_generation = await self.generate_audio_with_timestamps(
                script_id=script_id,
                idea_id=idea_id,
                phrases=script["phrases"]
            )
            
            # 3. Concaténer les fichiers audio
            combined_audio_path = os.path.join(audio_generation.audio_directory, "combined_audio.mp3")
            total_duration_ms = self._concatenate_audio_files(audio_generation.audio_directory, combined_audio_path)
            
            # 4. Vérifier si les timestamps existent déjà avant de les générer
            timestamps_collection = get_timestamps_collection()
            existing_timestamp = await timestamps_collection.find_one({"idea_id": idea_id}, {"_id": 0})
            
            if not existing_timestamp:
                # Générer les timestamps avec AssemblyAI seulement s'ils n'existent pas
                timestamp_document = await self.generate_timestamps_with_assemblyai(combined_audio_path, idea_id)
                await timestamps_collection.insert_one(timestamp_document.model_dump())
                print(f"✅ Generated {len(timestamp_document.timestamps)} timestamps for idea {idea_id}")
            else:
                print(f"✅ Timestamps already exist for idea {idea_id}, skipping generation")
            
            # 5. Sauvegarder les phrases audio dans le script
            await scripts_collection.update_one(
                {"id": script_id},
                {"$set": {"audio_phrases": [phrase.model_dump() for phrase in audio_generation.phrases]}}
            )
            
            # 6. Mettre à jour le statut de l'idée
            ideas_collection = get_ideas_collection()
            await ideas_collection.update_one(
                {"id": idea_id},
                {"$set": {"status": IdeaStatus.AUDIO_GENERATED}}
            )
            
            print(f"✅ Complete audio generation with timestamps for script {script_id}")
            print(f"📊 Generated {len(audio_generation.phrases)} audio phrases")
            
            return audio_generation
            
        except Exception as e:
            print(f"❌ Error in complete_audio_generation_with_timestamps: {str(e)}")
            raise
