"""
Service pour gérer la configuration et les statistiques ElevenLabs
"""

from typing import Dict, List
import os
from helpers.datetime_utils import start_of_day_utc
import traceback


class ElevenLabsConfigService:
    """
    Service pour gérer la configuration ElevenLabs et les statistiques
    """
    
    def __init__(self):
        pass
    
    async def get_keys_details(self) -> Dict:
        """
        Récupérer les détails de toutes les clés ElevenLabs configurées
        
        Returns:
            dict: Détails des clés ElevenLabs
        """
        try:
            from elevenlabs import ElevenLabs
            
            keys_details = []
            
            for i in range(1, 6):
                key = os.getenv(f"ELEVENLABS_API_KEY{i}")
                if key and key.startswith("sk_"):
                    try:
                        # Initialiser le client ElevenLabs
                        client = ElevenLabs(api_key=key)
                        
                        # Récupérer les infos du compte
                        user_info = client.user.get()
                        subscription = user_info.subscription
                        
                        keys_details.append({
                            "key_number": i,
                            "key": f"{key[:8]}...{key[-4:]}",  # Masquer la clé
                            "full_key": key,  # Pour usage interne seulement
                            "email": getattr(user_info, 'email', 'N/A'),
                            "first_name": getattr(user_info, 'first_name', 'N/A'),                
                            "character_count": subscription.character_count,
                            "character_limit": subscription.character_limit,
                            "characters_remaining": subscription.character_limit - subscription.character_count,
                            "tier": subscription.tier,
                            "status": subscription.status,
                            "next_character_count_reset_unix": subscription.next_character_count_reset_unix,
                        })
                    except Exception as e:
                        keys_details.append({
                            "key_number": i,
                            "key": f"{key[:8]}...{key[-4:]}",
                            "error": str(e),
                            "status": "error"
                        })
            
            return {
                "keys": keys_details,
                "total_keys": len(keys_details)
            }
            
        except Exception as e:
            print(f"❌ Error fetching ElevenLabs keys details: {str(e)}")
            traceback.print_exc()
            raise
    
    async def get_config(self) -> Dict:
        """
        Récupérer la configuration ElevenLabs
        
        Returns:
            dict: Configuration ElevenLabs
        """
        try:
            # Compter les clés disponibles
            api_keys = []
            for i in range(1, 6):
                key = os.getenv(f"ELEVENLABS_API_KEY{i}")
                if key and key.startswith("sk_"):
                    api_keys.append({
                        "index": i,
                        "configured": True,
                        "key_preview": key[:10] + "..." if len(key) > 10 else key
                    })
                else:
                    api_keys.append({
                        "index": i,
                        "configured": False
                    })
            
            voice_id = os.getenv("ELEVENLABS_VOICE_ID")
            voice_name = os.getenv("ELEVENLABS_VOICE_NAME")
            
            return {
                "api_keys": api_keys,
                "voice_id": voice_id,
                "voice_name": voice_name,
                "total_keys": len([k for k in api_keys if k["configured"]]),
                "voice_settings": {
                    "current_voice_id": voice_id,
                    "current_voice_name": voice_name,
                    "can_change": True
                }
            }
            
        except Exception as e:
            print(f"❌ Error fetching ElevenLabs config: {str(e)}")
            traceback.print_exc()
            raise
    
    async def get_stats(self) -> Dict:
        """
        Récupérer les statistiques d'utilisation ElevenLabs
        
        Returns:
            dict: Statistiques ElevenLabs
        """
        try:
            from database import get_scripts_collection
            
            # Compter les caractères générés aujourd'hui
            scripts_collection = get_scripts_collection()
            today_start = start_of_day_utc()
            
            # Compter les scripts générés aujourd'hui
            scripts_today = await scripts_collection.count_documents({
                "created_at": {"$gte": today_start}
            })
            
            # Estimer les caractères (moyenne ~200 caractères par script)
            estimated_chars_today = scripts_today * 200
            
            # Configuration des clés
            configured_keys = []
            for i in range(1, 6):
                key = os.getenv(f"ELEVENLABS_API_KEY{i}")
                if key and key.startswith("sk_"):
                    configured_keys.append(i)
            
            return {
                "keys_configured": len(configured_keys),
                "scripts_generated_today": scripts_today,
                "estimated_chars_today": estimated_chars_today,
                "quota_info": {
                    "estimated_chars_per_script": 200,
                    "free_tier_monthly": 10000,
                    "note": "Les quotas exacts nécessitent l'API ElevenLabs"
                },
                "rotation_status": {
                    "enabled": len(configured_keys) > 1,
                    "total_keys": len(configured_keys)
                }
            }
            
        except Exception as e:
            print(f"❌ Error fetching ElevenLabs stats: {str(e)}")
            traceback.print_exc()
            raise
