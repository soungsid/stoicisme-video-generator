"""
Service dédié à la gestion des sous-titres
Facilite la maintenance et les évolutions futures
"""
import re
import os
from moviepy.editor import TextClip
from typing import List, Dict, Optional
from models import TimestampItem
from database import get_timestamps_collection
from services.assemblyai_service import AssemblyAIService

# Configurer MoviePy pour ImageMagick
try:
    from config.moviepy_config import configure_moviepy
    configure_moviepy()
except Exception as e:
    print(f"⚠️  MoviePy config import failed: {e}")
    # Fallback: configuration directe
    os.environ['IMAGEMAGICK_BINARY'] = os.getenv('IMAGEMAGICK_BINARY', '/usr/bin/convert')

class SubtitleService:
    """Service de génération et gestion des sous-titres"""
    
    def __init__(self):
        # Polices disponibles dans le conteneur Docker
        # Ordre de préférence des polices
        available_fonts = [
            'DejaVu-Sans-Bold',
            'Liberation-Sans-Bold',
            'Noto-Sans-Bold',
            'Arial-Bold',
            'Helvetica-Bold'
        ]
        
        # Sélectionner la première police disponible
        selected_font = available_fonts[0]
        
        # Configuration par défaut des sous-titres
        self.default_config = {
            'fontsize': 50,
            'color': 'white',
            'bg_color': 'black',
            'font': selected_font,
            'margin': 60,  # Marge horizontale augmentée
            'bottom_offset': 120,  # Distance du bas de l'écran
            'stroke_color': 'black',
            'stroke_width': 2
        }
        
        # Variable d'environnement pour désactiver le traitement des sous-titres
        self.subtitles_enabled = os.getenv("SUBTITLES_ENABLED", "true").lower() == "true"
        self.assemblyai_service = AssemblyAIService()
        
        print(f"🎨 Subtitle Service initialized with font: {selected_font}")
        print(f"📝 Subtitles enabled: {self.subtitles_enabled}")
    
    def clean_text(self, text: str) -> str:
        """
        Nettoyer le texte des marqueurs ElevenLabs et autres artefacts
        
        Args:
            text: Texte brut avec possibles marqueurs
            
        Returns:
            Texte nettoyé
        """
        # Supprimer tous les marqueurs entre crochets: [laughs], [excited], etc.
        clean_text = re.sub(r'\[.*?\]', '', text)
        
        # Nettoyer les espaces multiples
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def create_subtitle_clip(
        self, 
        text: str, 
        start_time_ms: float, 
        duration_ms: float,
        video_width: int,
        video_height: int,
        config: dict = None
    ) -> TextClip:
        """
        Créer un clip de sous-titre pour une phrase
        
        Args:
            text: Texte du sous-titre
            start_time_ms: Temps de début en millisecondes
            duration_ms: Durée en millisecondes
            video_width: Largeur de la vidéo
            video_height: Hauteur de la vidéo
            config: Configuration optionnelle (override des valeurs par défaut)
            
        Returns:
            TextClip configuré
        """
        # Fusionner config par défaut avec config personnalisée
        cfg = {**self.default_config, **(config or {})}
        
        # Créer le TextClip
        txt_clip = TextClip(
            text,
            fontsize=cfg['fontsize'],
            color=cfg['color'],
            bg_color=cfg['bg_color'],
            font=cfg['font'],
            size=(video_width - cfg['margin'], None),
            method='caption'
        )
        
        # Positionner en bas de l'écran
        txt_clip = txt_clip.set_position(('center', video_height - cfg['bottom_offset']))
        txt_clip = txt_clip.set_start(start_time_ms / 1000)
        txt_clip = txt_clip.set_duration(duration_ms / 1000)
        
        return txt_clip
    
    def create_subtitle_clips(
        self, 
        phrases: List[TimestampItem], 
        video_width: int, 
        video_height: int,
        config: dict = None
    ) -> List[TextClip]:
        """
        Créer tous les clips de sous-titres pour une liste de phrases
        
        Args:
            phrases: Liste des phrases avec timestamps
            video_width: Largeur de la vidéo
            video_height: Hauteur de la vidéo
            config: Configuration optionnelle
            
        Returns:
            Liste de TextClip
        """
        subtitle_clips = []
        
        for phrase in phrases:
            # Nettoyer le texte
            clean_text = self.clean_text(phrase.text)
            
            # Ne créer un sous-titre que si du texte reste
            if not clean_text:
                continue
            
            # Créer le clip
            txt_clip = self.create_subtitle_clip(
                text=clean_text,
                start_time_ms=phrase.start_time_ms,
                duration_ms=(phrase.end_time_ms - phrase.start_time_ms),
                video_width=video_width,
                video_height=video_height,
                config=config
            )
            
            subtitle_clips.append(txt_clip)
        
        print(f"📝 {len(subtitle_clips)} sous-titres créés (marqueurs ElevenLabs nettoyés)")
        return subtitle_clips
    
    
    async def add_subtitles_to_video(
        self,
        final_video,
        idea_id: str,
        config: dict = None
    ):
        """
        Ajouter les sous-titres à une vidéo finale en centralisant toute la logique
        
        Args:
            final_video: Vidéo finale (MoviePy VideoClip)
            idea_id: ID de l'idée
            config: Configuration optionnelle pour les sous-titres
            
        Returns:
            Vidéo avec sous-titres ajoutés si activés, vidéo originale sinon
        """
        # Vérifier si les sous-titres sont désactivés
        if not self.subtitles_enabled:
            print("📝 Sous-titres désactivés (SUBTITLES_ENABLED=false)")
            return final_video
        
        try:
            # Vérifier si les timestamps existent déjà
            timestamps_collection = get_timestamps_collection()
            existing_timestamp = await timestamps_collection.find_one({"idea_id": idea_id}, {"_id": 0})
            
            if not existing_timestamp:
                print(f"❌ Aucun timestamp trouvé pour l'idée {idea_id}")
                return final_video
            
            print(f"✅ Timestamps existants trouvés pour l'idée {idea_id}")
            
            # Créer les clips de sous-titres à partir des timestamps
            print(f"📝 Génération des sous-titres pour la vidéo...")
            subtitle_clips = self.create_subtitle_clips(
                existing_timestamp["timestamps"],
                int(final_video.w),
                int(final_video.h),
                config
            )
            
            if subtitle_clips:
                from moviepy.editor import CompositeVideoClip
                final_video_with_subtitles = CompositeVideoClip([final_video] + subtitle_clips)
                print(f"✅ {len(subtitle_clips)} sous-titres ajoutés à la vidéo")
                return final_video_with_subtitles
            else:
                print("📝 Aucun sous-titre généré (phrases vides ou nettoyées)")
                return final_video
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout des sous-titres: {str(e)}")
            return final_video
    
    async def process_subtitles_for_idea(
        self,
        idea_id: str,
        audio_path: str
    ) -> bool:
        """
        Traiter les sous-titres pour une idée (générer les timestamps si nécessaire)
        
        Args:
            idea_id: ID de l'idée
            audio_path: Chemin vers le fichier audio
            
        Returns:
            True si le traitement a réussi, False sinon
        """
        # Vérifier si les sous-titres sont désactivés
        if not self.subtitles_enabled:
            print(f"📝 Sous-titres désactivés pour l'idée {idea_id}")
            return True
        
        try:
            # Vérifier si les timestamps existent déjà
            timestamps_collection = get_timestamps_collection()
            existing_timestamp = await timestamps_collection.find_one({"idea_id": idea_id}, {"_id": 0})
            
            if existing_timestamp:
                print(f"✅ Timestamps existants pour l'idée {idea_id}")
                return True
            
            # Générer les timestamps avec AssemblyAI
            print(f"🎯 Génération des timestamps pour l'idée {idea_id}")
            timestamp_document = await self.assemblyai_service.transcribe_and_get_timestamps(audio_path, idea_id)
            
            if timestamp_document:
                # Sauvegarder les timestamps
                await timestamps_collection.insert_one(timestamp_document.model_dump())
                print(f"✅ {len(timestamp_document.timestamps)} timestamps générés pour l'idée {idea_id}")
                return True
            else:
                print(f"❌ Échec de la génération des timestamps pour l'idée {idea_id}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement des sous-titres pour l'idée {idea_id}: {str(e)}")
            return False
