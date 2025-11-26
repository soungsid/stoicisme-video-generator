import os
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
        self.audio_dir = os.path.join(self.resources_dir, "audio")
        self.images_dir = os.path.join(self.resources_dir, "images")
        self.subtitles_dir = os.path.join(self.resources_dir, "subtitles")
        
        # Créer les répertoires s'ils n'existent pas
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crée les répertoires de ressources s'ils n'existent pas"""
        directories = [
            self.resources_dir,
            self.template_dir,
            self.videos_dir,
            self.audio_dir,
            self.images_dir,
            self.subtitles_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Nettoie un nom de fichier pour le rendre sûr pour le système de fichiers
        """
        # Remplacer les caractères non autorisés par des underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Supprimer les espaces multiples et les espaces en début/fin
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        # Limiter la longueur
        return sanitized[:100]
    
    def get_idea_directories(self, idea_id: str, idea_title: str = None) -> Dict[str, str]:
        """
        Retourne les répertoires pour une idée spécifique
        
        Args:
            idea_id: L'ID de l'idée
            idea_title: Le titre de l'idée (optionnel, utilisé pour nommer le dossier)
            
        Returns:
            Dictionnaire avec les chemins des répertoires
        """
        # Créer un nom de dossier basé sur l'ID et le titre (si disponible)
        if idea_title:
            safe_title = slugify(idea_id)
            folder_name = safe_title
        else:
            folder_name = idea_id
        
        # Répertoire principal de l'idée
        idea_dir = os.path.join(self.videos_dir, folder_name)
        
        # Sous-répertoires
        video_directory = idea_dir
        audio_directory = os.path.join(idea_dir, "audio")
        image_directory = os.path.join(idea_dir, "images")
        subtitle_directory = os.path.join(idea_dir, "subtitles")
        
        # Créer les répertoires
        for directory in [idea_dir, audio_directory, image_directory, subtitle_directory]:
            os.makedirs(directory, exist_ok=True)
        
        return {
            "video_directory": video_directory,
            "audio_directory": audio_directory,
            "image_directory": image_directory,
            "subtitle_directory": subtitle_directory,
            "idea_directory": idea_dir
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
    
    def get_resource_path(self, resource_type: str, filename: str) -> str:
        """
        Retourne le chemin complet pour une ressource spécifique
        
        Args:
            resource_type: Type de ressource ('video', 'audio', 'image', 'subtitle')
            filename: Nom du fichier
            
        Returns:
            Chemin complet vers la ressource
        """
        if resource_type == 'video':
            return os.path.join(self.videos_dir, filename)
        elif resource_type == 'audio':
            return os.path.join(self.audio_dir, filename)
        elif resource_type == 'image':
            return os.path.join(self.images_dir, filename)
        elif resource_type == 'subtitle':
            return os.path.join(self.subtitles_dir, filename)
        else:
            raise ValueError(f"Type de ressource non supporté: {resource_type}")
    
    def get_resources_dir(self) -> str:
        """Retourne le répertoire racine des ressources"""
        return self.resources_dir
    
    def get_template_dir(self) -> str:
        """Retourne le répertoire des templates"""
        return self.template_dir
    
    def get_videos_dir(self) -> str:
        """Retourne le répertoire des vidéos"""
        return self.videos_dir
    
    def get_audio_dir(self) -> str:
        """Retourne le répertoire des fichiers audio"""
        return self.audio_dir
    
    def get_images_dir(self) -> str:
        """Retourne le répertoire des images"""
        return self.images_dir
    
    def get_subtitles_dir(self) -> str:
        """Retourne le répertoire des sous-titres"""
        return self.subtitles_dir
