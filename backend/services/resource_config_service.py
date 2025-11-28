import os
from pathlib import Path
from typing import Dict
import re

from slugify import slugify

class ResourceConfigService:
    """
    Service centralisé pour la gestion des chemins de ressources
    Gère les répertoires pour les vidéos, audio, images et sous-titres
    """
    
    def __init__(self):
        self.resources_dir = os.getenv("RESOURCES_DIR", "/app/ressources")
        self.template_dir = os.path.join(self.resources_dir, "video-template")
        self.videos_dir = os.path.join(self.resources_dir, "videos")
        
        # Créer les répertoires s'ils n'existent pas
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crée les répertoires de ressources s'ils n'existent pas"""
        directories = [
            self.resources_dir,
            self.template_dir,
            self.videos_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    
    def get_idea_directories(self, idea_id: str, idea_title: str = None) -> Dict[str, str]:
        if idea_title:
            safe_title = slugify(idea_title)
            folder_name = safe_title
        else:
            folder_name = idea_id

        base_dir = Path(self.videos_dir)  # convertit en Path OS-safe

        idea_dir = base_dir / folder_name
        audio_dir = idea_dir / "audio"
        image_dir = idea_dir / "images"
        subtitle_dir = idea_dir / "subtitles"

        # Création des dossiers
        for d in [idea_dir, audio_dir, image_dir, subtitle_dir]:
            d.mkdir(parents=True, exist_ok=True)

        return {
            "video_directory": str(idea_dir),
            "audio_directory": str(audio_dir),
            "image_directory": str(image_dir),
            "subtitle_directory": str(subtitle_dir),
            "idea_directory": str(idea_dir),
        }
    
    def get_template_files(self) -> list:
        """
        Retourne la liste des fichiers de template disponibles
        """
        try:
            files = os.listdir(self.template_dir)
            # Filtrer pour ne garder que les fichiers vidéo
            video_files = [f for f in files if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
            return [os.path.join(self.template_dir, f) for f in video_files]
        except FileNotFoundError:
            return []
    
    
    def get_resources_dir(self) -> str:
        """Retourne le répertoire racine des ressources"""
        return self.resources_dir
    
    def get_template_dir(self) -> str:
        """Retourne le répertoire des templates"""
        return self.template_dir
    
    def get_videos_dir(self) -> str:
        """Retourne le répertoire des vidéos"""
        return self.videos_dir
    
if __name__ == "__main__":
    resourceConfigService = ResourceConfigService()
    print(f" {resourceConfigService.get_idea_directories("", "un titre avec de.chao,edede")}")