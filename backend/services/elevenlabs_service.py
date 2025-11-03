import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from typing import List, Tuple
import asyncio
from functools import lru_cache

class ElevenLabsService:
    """
    Service pour gérer les appels à ElevenLabs avec rotation des 5 clés API
    """
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "Bj9UqZbhQsanLzgalpEG")
        
    def _load_api_keys(self) -> List[str]:
        """Charger toutes les clés API ElevenLabs disponibles"""
        keys = []
        for i in range(1, 6):
            key = os.getenv(f"ELEVENLABS_API_KEY{i}")
            if key and key.startswith("sk_"):
                keys.append(key)
        
        if not keys:
            raise ValueError("No valid ElevenLabs API keys found in environment")
        
        print(f"✅ Loaded {len(keys)} ElevenLabs API keys")
        return keys
    
    def _get_next_client(self) -> ElevenLabs:
        """Obtenir le prochain client ElevenLabs avec rotation"""
        api_key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        
        print(f"Using ElevenLabs key #{self.current_key_index + 1}/{len(self.api_keys)}")
        return ElevenLabs(api_key=api_key)
    
    async def generate_audio(self, text: str, output_path: str) -> Tuple[str, int]:
        """
        Générer l'audio pour un texte donné
        Retourne: (chemin du fichier, durée en millisecondes)
        """
        try:
            client = self._get_next_client()
            
            # Générer l'audio
            audio = client.generate(
                text=text,
                voice=self.voice_id,
                model="eleven_multilingual_v2"
            )
            
            # Sauvegarder l'audio
            save(audio, output_path)
            
            # Calculer la durée avec pydub
            from pydub import AudioSegment
            audio_segment = AudioSegment.from_mp3(output_path)
            duration_ms = len(audio_segment)
            
            print(f"✅ Generated audio: {output_path} ({duration_ms}ms)")
            return output_path, duration_ms
            
        except Exception as e:
            print(f"❌ Error generating audio: {str(e)}")
            raise
    
    async def generate_multiple_audios(self, phrases: List[str], output_dir: str) -> List[Tuple[str, int]]:
        """
        Générer plusieurs audios en parallèle avec rotation des clés
        """
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        for i, phrase in enumerate(phrases):
            output_path = os.path.join(output_dir, f"phrase_{i:03d}.mp3")
            path, duration = await self.generate_audio(phrase, output_path)
            results.append((path, duration))
            
            # Petit délai pour éviter rate limiting
            await asyncio.sleep(0.5)
        
        return results
