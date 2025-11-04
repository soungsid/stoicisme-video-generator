import os
import random
from typing import Dict
from models import Video, VideoType
from slugify import slugify
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip
from pydub import AudioSegment
import subprocess

class VideoService:
    """
    Service pour assembler les vidéos avec audio et sous-titres
    """
    
    def __init__(self):
        self.template_dir = "../ressources/video-template"
        self.videos_dir = "../ressources/videos"
    
    def get_video_directory(self, title: str, subdir: str = None) -> str:
        """Obtenir le répertoire pour une vidéo"""
        slug = slugify(title)
        video_dir = os.path.join(self.videos_dir, slug)
        
        if subdir:
            video_dir = os.path.join(video_dir, subdir)
        
        os.makedirs(video_dir, exist_ok=True)
        return video_dir
    
    def _select_random_template(self) -> str:
        """Sélectionner un template vidéo aléatoire"""
        templates = [f for f in os.listdir(self.template_dir) if f.endswith('.mp4')]
        
        if not templates:
            raise ValueError("No video templates found")
        
        selected = random.choice(templates)
        template_path = os.path.join(self.template_dir, selected)
        print(f"Selected template: {selected}")
        return template_path
    
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
    
    def _create_subtitle_clips(self, phrases: list, video_width: int, video_height: int):
        """Créer les clips de sous-titres"""
        subtitle_clips = []
        
        for phrase in phrases:
            # Créer un TextClip pour chaque phrase
            txt_clip = TextClip(
                phrase["phrase_text"],
                fontsize=40,
                color='white',
                bg_color='black',
                font='Arial-Bold',
                size=(video_width - 40, None),
                method='caption'
            )
            
            # Positionner en bas de l'écran
            txt_clip = txt_clip.set_position(('center', video_height - 100))
            txt_clip = txt_clip.set_start(phrase["start_time_ms"] / 1000)
            txt_clip = txt_clip.set_duration(phrase["duration_ms"] / 1000)
            
            subtitle_clips.append(txt_clip)
        
        return subtitle_clips
    
    async def generate_video(
        self,
        idea: Dict,
        script: Dict
    ) -> Video:
        """
        Générer la vidéo finale avec audio et sous-titres
        """
        try:
            title = idea["title"]
            video_type = VideoType(idea["video_type"])
            
            # Répertoires
            video_dir = self.get_video_directory(title)
            audio_dir = self.get_video_directory(title, "audio")
            
            # Sélectionner un template
            template_path = self._select_random_template()
            
            # Concaténer les audios
            combined_audio_path = os.path.join(video_dir, "combined_audio.mp3")
            audio_duration_ms = self._concatenate_audio_files(audio_dir, combined_audio_path)
            
            # Charger le template vidéo
            video_clip = VideoFileClip(template_path)
            
            # Boucler la vidéo pour correspondre à la durée audio
            audio_duration_sec = audio_duration_ms / 1000
            if video_clip.duration < audio_duration_sec:
                # Boucler la vidéo
                n_loops = int(audio_duration_sec / video_clip.duration) + 1
                video_clip = video_clip.loop(n=n_loops)
            
            # Couper à la durée exacte
            video_clip = video_clip.subclip(0, audio_duration_sec)
            
            # Charger l'audio
            audio_clip = AudioFileClip(combined_audio_path)
            
            # Ajouter l'audio à la vidéo
            video_clip = video_clip.set_audio(audio_clip)
            
            # TODO: Ajouter les sous-titres (nécessite ImageMagick)
            # Pour l'instant, on génère sans sous-titres
            
            # Chemin de sortie
            output_path = os.path.join(video_dir, f"{slugify(title)}.mp4")
            
            # Exporter la vidéo
            video_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=24,
                preset='medium'
            )
            
            # Fermer les clips
            video_clip.close()
            audio_clip.close()
            
            print(f"✅ Video generated: {output_path}")
            
            # Créer l'objet Video
            video = Video(
                idea_id=idea["id"],
                script_id=script["id"],
                audio_id=script["id"],  # On utilise script_id comme audio_id
                title=title,
                video_type=video_type,
                video_path=output_path,
                duration_seconds=audio_duration_sec
            )
            
            return video
            
        except Exception as e:
            print(f"❌ Error generating video: {str(e)}")
            raise
