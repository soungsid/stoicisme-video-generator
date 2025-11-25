import os
import random
from typing import Dict
from database import get_videos_collection
from models import Video, VideoType, IdeaStatus
from slugify import slugify
from moviepy.editor import VideoFileClip, AudioFileClip,  CompositeVideoClip
from pydub import AudioSegment
from services.subtitle_service import SubtitleService
from services.resource_config_service import ResourceConfigService

class VideoService:
    """
    Service pour assembler les vidéos avec audio et sous-titres
    """
    
    def __init__(self):
        self.REACT_APP_BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8001")
        self.resource_config = ResourceConfigService()
        self.subtitle_service = SubtitleService()  # Service de sous-titres
    
    def get_video_directory(self, idea_id: str, title: str) -> str:
        """Obtenir le répertoire pour une vidéo"""
        directories = self.resource_config.get_idea_directories(idea_id, title)
        return directories["video_directory"]
    
    def _select_random_template(self) -> str:
        """Sélectionner un template vidéo aléatoire"""
        templates = self.resource_config.get_template_files()
        
        if not templates:
            raise ValueError("No video templates found")
        
        selected = random.choice(templates)
        print(f"Selected template: {os.path.basename(selected)}")
        return selected
    
    def _get_combined_audio_path(self, audio_dir: str) -> str:
        """Obtenir le chemin de l'audio concaténé"""
        combined_audio_path = os.path.join(audio_dir, "combined_audio.mp3")
        if not os.path.exists(combined_audio_path):
            raise ValueError(f"Combined audio file not found: {combined_audio_path}")
        return combined_audio_path
    
    async def generate_video(
        self,
        script_id: str
    ) -> Video:
        """
        Générer la vidéo finale avec audio et sous-titres
        
        Args:
            script_id: ID du script dans MongoDB
            
        Returns:
            Objet Video créé
            
        Cette méthode:
        1. Récupère le script et l'idée depuis MongoDB
        2. Génère la vidéo avec audio et sous-titres
        3. Retourne l'objet Video (non sauvegardé en DB)
        """
        try:
            from database import get_scripts_collection, get_ideas_collection
            
            # 1. Récupérer le script depuis MongoDB
            scripts_collection = get_scripts_collection()
            script = await scripts_collection.find_one({"id": script_id}, {"_id": 0})
            
            if not script:
                raise ValueError(f"Script {script_id} not found")
            
            # 2. Récupérer l'idée associée
            idea_id = script.get("idea_id")
            if not idea_id:
                raise ValueError(f"Script {script_id} has no associated idea")
            
            ideas_collection = get_ideas_collection()
            idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
            
            if not idea:
                raise ValueError(f"Idea {idea_id} not found")
            
            # 3. Générer la vidéo
            title = idea["title"]
            video_type = VideoType(idea["video_type"])
            
            print(f"🎬 Début de la génération vidéo pour: {title}")
            
            # Répertoires
            video_dir = self.get_video_directory(idea_id, title)
            directories = self.resource_config.get_idea_directories(idea_id, title)
            audio_dir = directories["audio_directory"]
            
            # Sélectionner un template
            print("📹 Sélection d'un template vidéo aléatoire...")
            template_path = self._select_random_template()
            
            # Utiliser l'audio déjà concaténé
            print("🎵 Utilisation de l'audio concaténé...")
            combined_audio_path = self._get_combined_audio_path(audio_dir)
            
            # Obtenir la durée de l'audio concaténé
            audio_clip = AudioFileClip(combined_audio_path)
            audio_duration_sec = audio_clip.duration
            audio_duration_ms = int(audio_duration_sec * 1000)
            audio_clip.close()
            
            print(f"✅ Audio concaténé utilisé: {audio_duration_sec:.2f}s")
            
            # Charger le template vidéo
            print("📽️ Chargement du template vidéo...")
            video_clip = VideoFileClip(template_path)
            
            # Boucler la vidéo pour correspondre à la durée audio
            audio_duration_sec = audio_duration_ms / 1000
            if video_clip.duration < audio_duration_sec:
                print(f"🔄 Bouclage de la vidéo (durée template: {video_clip.duration:.2f}s → {audio_duration_sec:.2f}s)")
                n_loops = int(audio_duration_sec / video_clip.duration) + 1
                video_clip = video_clip.loop(n=n_loops)
            
            # Couper à la durée exacte
            video_clip = video_clip.subclip(0, audio_duration_sec)
            
            # Charger l'audio
            print("🎧 Ajout de l'audio à la vidéo...")
            audio_clip = AudioFileClip(combined_audio_path)
            
            # Ajouter l'audio à la vidéo
            final_video = video_clip.set_audio(audio_clip)
            
            # Ajouter les sous-titres via le service centralisé
            print("📝 Ajout des sous-titres via le service centralisé...")
            final_video = await self.subtitle_service.add_subtitles_to_video(
                final_video=final_video,
                idea_id=idea_id
            )
            
            # Chemin de sortie
            output_path = os.path.join(video_dir, f"{slugify(title)}.mp4")
            
            # Exporter la vidéo
            print("⏳ Exportation de la vidéo (cela peut prendre plusieurs minutes)...")
            print("   Codec: libx264 | Audio: aac | FPS: 24 | Preset: medium")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=24,
                preset='medium',
                threads=4,
                logger=None
            )
            
            # Fermer les clips
            final_video.close()
            if audio_clip:
                audio_clip.close()
            
            print(f"✅ Vidéo générée avec succès: {output_path}")
            print(f"📊 Durée finale: {audio_duration_sec:.2f}s")
            
            # Créer l'URL accessible pour le frontend
            # Convertir /app/ressources/videos/slug/video.mp4 → /media/videos/slug/video.mp4
            relative_path = os.path.relpath(output_path, self.resource_config.get_resources_dir())
            video_url = f"{self.REACT_APP_BACKEND_URL}/media/{relative_path}"
            
            # Créer l'objet Video
            video = Video(
                idea_id=idea["id"],
                script_id=script["id"],
                audio_id=script["id"],  # On utilise script_id comme audio_id
                title=title,
                video_type=video_type,
                video_path=video_url,  # URL accessible via /media
                video_relative_path=output_path,
                duration_seconds=audio_duration_sec,
                youtube_description=script["youtube_description"]
            )
            
            # Sauvegarder la vidéo
            videos_collection = get_videos_collection()
            await videos_collection.insert_one(video.model_dump())
             # Mettre à jour le statut de l'idée
            await ideas_collection.update_one(
                {"id": idea_id},
                {"$set": {"status": IdeaStatus.VIDEO_GENERATED}}
            )
            
            return video
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération vidéo: {str(e)}")
            raise
