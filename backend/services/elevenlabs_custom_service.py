import os
import elevenlabs
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from typing import List, Tuple, Set
import asyncio
from functools import lru_cache
import time
import json

class ElevenLabsService:
    """
    Service pour gérer les appels à ElevenLabs avec rotation des 5 clés API
    et gestion des erreurs de crédits
    """
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        #t8BrjWUT5Z23DLLBzbuY voix feminine
        #Bj9UqZbhQsanLzgalpEG austin
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "NOpBlnGInO9m6vDvFkFC")
        self.exhausted_keys: Set[str] = set()
        self.last_cleanup_time = time.time()
        self.cleanup_interval = 24 * 60 * 60  # 24 heures en secondes
        
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
    
    def _cleanup_exhausted_keys(self):
        """Nettoyer la liste des clés épuisées tous les 24 heures"""
        current_time = time.time()
        if current_time - self.last_cleanup_time >= self.cleanup_interval:
            print(f"🧹 Cleaning up exhausted keys list (was {len(self.exhausted_keys)} keys)")
            self.exhausted_keys.clear()
            self.last_cleanup_time = current_time
    
    def _is_key_exhausted(self, api_key: str) -> bool:
        """Vérifier si une clé API est épuisée"""
        return api_key in self.exhausted_keys
    
    def _mark_key_as_exhausted(self, api_key: str):
        """Marquer une clé API comme épuisée"""
        if api_key not in self.exhausted_keys:
            self.exhausted_keys.add(api_key)
            print(f"⚠️  Marked API key as exhausted: {api_key[:10]}...")
    
    def _get_available_keys(self) -> List[str]:
        """Obtenir la liste des clés API disponibles (non épuisées)"""
        available_keys = [key for key in self.api_keys if not self._is_key_exhausted(key)]
        if not available_keys:
            raise ValueError("All ElevenLabs API keys are exhausted. Please add new keys or wait for daily reset.")
        return available_keys
    
    def _get_next_client(self) -> ElevenLabs:
        """Obtenir le prochain client ElevenLabs avec rotation"""
        # Nettoyer les clés épuisées si nécessaire
        self._cleanup_exhausted_keys()
        
        # Obtenir les clés disponibles
        available_keys = self._get_available_keys()
        
        # Si toutes les clés sont épuisées, on réinitialise l'index
        if self.current_key_index >= len(available_keys):
            self.current_key_index = 0
        
        api_key = available_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(available_keys)
        
        print(f"🔑 Using ElevenLabs key #{self.current_key_index + 1}/{len(available_keys)} (total: {len(self.api_keys)}, exhausted: {len(self.exhausted_keys)})")
        return ElevenLabs(api_key=api_key)
    
    def _is_credit_error(self, error_message: str) -> bool:
        """
        Détecter si l'erreur est liée aux crédits épuisés
        """
        credit_indicators = [
            "insufficient credits",
            "not enough credits",
            "quota exceeded",
            "quota limit",
            "character limit",
            "character quota",
            "monthly character limit",
            "monthly quota",
            "usage limit",
            "limit exceeded"
        ]
        
        error_lower = error_message.lower()
        return any(indicator in error_lower for indicator in credit_indicators)
    
    def _handle_elevenlabs_error(self, error: Exception, current_api_key: str):
        """
        Gérer les erreurs ElevenLabs et détecter les problèmes de crédits
        """
        error_message = str(error)
        print(f"🔍 Analyzing ElevenLabs error: {error_message}")
        
        # Vérifier si c'est une erreur de crédits
        if self._is_credit_error(error_message):
            print(f"💳 Credit limit detected for API key: {current_api_key[:10]}...")
            self._mark_key_as_exhausted(current_api_key)
            raise Exception(f"ElevenLabs credit limit reached for this API key. Key has been temporarily disabled.")
        else:
            # Autres erreurs (authentification, réseau, etc.)
            print(f"❌ Other ElevenLabs error: {error_message}")
            raise error
    
    async def generate_audio(self, text: str, output_path: str, max_retries: int = 3) -> Tuple[str, int]:
        """
        Générer l'audio pour un texte donné avec retry automatique en cas d'erreur de crédits
        Retourne: (chemin du fichier, durée en millisecondes)
        """
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"🎵 Generating audio {output_path} for text: {text[:100]}... (attempt {retry_count + 1}/{max_retries})")
                
                # Obtenir le client avec la clé actuelle
                client = self._get_next_client()
                
                # Stocker la clé actuelle pour la gestion d'erreur
                available_keys = self._get_available_keys()
                current_api_key = available_keys[(self.current_key_index - 1) % len(available_keys)]
                
                try:
                    # Générer l'audio
                    audio = client.text_to_speech.convert(
                        text="[excited] " + text,
                        voice_id=self.voice_id,
                        model_id="eleven_v3",
                        output_format="mp3_44100_128"  
                    )
                    print("✅ Audio generated successfully. Next step: saving audio")
                    
                    # Sauvegarder l'audio
                    save(audio, output_path)
                    
                    # Calculer la durée avec pydub
                    from pydub import AudioSegment
                    audio_segment = AudioSegment.from_mp3(output_path)
                    duration_ms = len(audio_segment)
                    
                    print(f"✅ Generated audio: {output_path} ({duration_ms}ms)")
                    return output_path, duration_ms
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    # Gérer l'erreur ElevenLabs spécifique
                    error_message = str(e)
                    
                    # Vérifier si c'est une erreur de crédits
                    if self._is_credit_error(error_message):
                        print(f"💳 Credit limit detected for API key: {current_api_key[:10]}...")
                        self._mark_key_as_exhausted(current_api_key)
                        
                        # Si c'est une erreur de crédits, on réessaie avec la clé suivante
                        retry_count += 1
                        print(f"🔄 Retrying with next API key... ({retry_count}/{max_retries})")
                        continue
                    else:
                        # Autres erreurs (authentification, réseau, etc.) - on propage l'erreur
                        print(f"❌ Other ElevenLabs error: {error_message}")
                        raise e
                        
            except Exception as e:
                # Si on arrive ici, c'est une erreur non liée aux crédits ou toutes les retries ont échoué
                if retry_count >= max_retries - 1:
                    print(f"❌ Max retries reached. Error generating audio: {str(e)}")
                    raise
                else:
                    retry_count += 1
                    print(f"🔄 Retrying... ({retry_count}/{max_retries})")
                    continue
        
        # Si on arrive ici, toutes les retries ont échoué
        raise Exception(f"Failed to generate audio after {max_retries} attempts")
    
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
    
async def main():
    elevenlabs_service = ElevenLabsService()
    text = """
    Un jeune couple venait d’emménager. Un matin, en prenant leur petit-déjeuner, la jeune femme vit sa voisine étendre son linge. « Son linge n’est pas propre, » dit-elle. « Elle ne sait pas bien laver. Elle devrait utiliser une meilleure lessive. » Son mari resta silencieux. Chaque fois que la voisine suspendait son linge, la jeune femme répétait les mêmes critiques. Un mois plus tard, elle fut étonnée de voir le linge parfaitement propre. « Regarde ! Elle a enfin appris à laver correctement. Qui a bien pu lui montrer ? » Son mari répondit calmement : « Je me suis levé tôt et j’ai nettoyé nos fenêtres. » La vie fonctionne ainsi : ce que nous percevons chez les autres dépend de la clarté de notre propre regard. Ne juge pas trop vite, surtout si ta vision est obscurcie par la colère, la jalousie ou la négativité. Juger quelqu’un ne dit pas qui il est, mais qui tu es.
    """
    await elevenlabs_service.generate_audio(text, "sss.mp3")
    
if __name__ == "__main__":
    asyncio.run(main())
