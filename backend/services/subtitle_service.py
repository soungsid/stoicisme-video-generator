"""
Service dédié à la gestion des sous-titres
Facilite la maintenance et les évolutions futures
"""
import re
from moviepy.editor import TextClip
from typing import List, Dict

class SubtitleService:
    """Service de génération et gestion des sous-titres"""
    
    def __init__(self):
        # Configuration par défaut des sous-titres
        self.default_config = {
            'fontsize': 40,
            'color': 'white',
            'bg_color': 'black',
            'font': 'Arial-Bold',
            'margin': 40,  # Marge horizontale
            'bottom_offset': 100  # Distance du bas de l'écran
        }
    
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
        phrases: List[Dict], 
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
            clean_text = self.clean_text(phrase["phrase_text"])
            
            # Ne créer un sous-titre que si du texte reste
            if not clean_text:
                continue
            
            # Créer le clip
            txt_clip = self.create_subtitle_clip(
                text=clean_text,
                start_time_ms=phrase["start_time_ms"],
                duration_ms=phrase["duration_ms"],
                video_width=video_width,
                video_height=video_height,
                config=config
            )
            
            subtitle_clips.append(txt_clip)
        
        print(f"📝 {len(subtitle_clips)} sous-titres créés (marqueurs ElevenLabs nettoyés)")
        return subtitle_clips
    
    def validate_subtitle_timing(self, phrases: List[Dict]) -> bool:
        """
        Valider que les timings des sous-titres sont cohérents
        
        Args:
            phrases: Liste des phrases avec timestamps
            
        Returns:
            True si valide, False sinon
        """
        for i, phrase in enumerate(phrases):
            # Vérifier que les champs requis existent
            required_fields = ["phrase_text", "start_time_ms", "duration_ms"]
            if not all(field in phrase for field in required_fields):
                print(f"❌ Phrase {i} manque des champs requis")
                return False
            
            # Vérifier que la durée est positive
            if phrase["duration_ms"] <= 0:
                print(f"❌ Phrase {i} a une durée invalide: {phrase['duration_ms']}ms")
                return False
            
            # Vérifier que le temps de début est positif
            if phrase["start_time_ms"] < 0:
                print(f"❌ Phrase {i} a un temps de début invalide: {phrase['start_time_ms']}ms")
                return False
        
        print(f"✅ Validation des timings: {len(phrases)} phrases OK")
        return True
    
    def get_total_duration(self, phrases: List[Dict]) -> float:
        """
        Calculer la durée totale couverte par les sous-titres
        
        Args:
            phrases: Liste des phrases avec timestamps
            
        Returns:
            Durée totale en secondes
        """
        if not phrases:
            return 0.0
        
        last_phrase = max(phrases, key=lambda p: p["start_time_ms"] + p["duration_ms"])
        total_ms = last_phrase["start_time_ms"] + last_phrase["duration_ms"]
        
        return total_ms / 1000
