import os
import assemblyai as aai
from typing import Optional
from models import Timestamp, TimestampItem

# Appelle l'api de assemblyai afin de generer la transcription et recuperer un fichier srt
NB_CARACTERE_PER_CAPTION = 80
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY", "c7dce2def45841bdb9d66f0cf8866b51")

transcriber = aai.Transcriber()




class AssemblyAIService:
    """Service pour gérer les opérations AssemblyAI avec encapsulation des données"""
    
    def __init__(self):
        self.transcriber = aai.Transcriber()
        
    def _transcribe(self, audio_path,  language_code="fr", generate_subtitles=True, nb_caracter_per_caption=NB_CARACTERE_PER_CAPTION,):
        config = aai.TranscriptionConfig(speaker_labels=True, language_code=language_code)

        transcript = self.transcriber.transcribe(audio_path, config)
        srt_path = audio_path.replace(".mp3", f"_{language_code}.srt")

        if transcript.error:
            print(transcript.error)
        else:
            if generate_subtitles:
                f = open(srt_path, "a", encoding="UTF8")
                f.write(transcript.export_subtitles_srt(chars_per_caption=nb_caracter_per_caption))
                f.close()
        return transcript,srt_path
    
    async def transcribe_and_get_timestamps(self, audio_path: str, idea_id: str) -> Optional[Timestamp]:
        """
        Transcrire l'audio et retourner directement l'objet Timestamp
        
        Args:
            audio_path: Chemin vers le fichier audio
            idea_id: ID de l'idée
            
        Returns:
            Objet Timestamp contenant tous les timestamps, None en cas d'erreur
        """
        try:
            print(f"🎯 Transcription AssemblyAI pour l'idée {idea_id}")
            
            # Utiliser AssemblyAI pour transcrire
            (transcript, srt) = self._transcribe(audio_path)
            
            # Extraire les timestamps du transcript et les transformer en objets TimestampItem
            timestamp_items = []
            total_duration_ms = 0
            
            for utterance in transcript.utterances:
                timestamp_item = TimestampItem(
                    text=utterance.text,
                    start_time_ms=int(utterance.start),
                    end_time_ms=int(utterance.end),
                    confidence=utterance.confidence
                )
                timestamp_items.append(timestamp_item)
                
                # Calculer la durée totale
                if int(utterance.end) > total_duration_ms:
                    total_duration_ms = int(utterance.end)
            
            # Créer l'objet Timestamp
            timestamp_document = Timestamp(
                idea_id=idea_id,
                timestamps=timestamp_items,
                total_duration_ms=total_duration_ms
            )
            
            print(f"✅ {len(timestamp_items)} timestamps générés pour l'idée {idea_id}")
            return timestamp_document
            
        except Exception as e:
            print(f"❌ Erreur lors de la transcription AssemblyAI: {str(e)}")
            return None
