"""
Service pour gérer la configuration et les statistiques YouTube
"""

from typing import Dict
from database import get_config_collection, get_videos_collection
from helpers.datetime_utils import now_utc, start_of_day_utc
import traceback


class YoutubeConfigService:
    """
    Service pour gérer la configuration YouTube et les statistiques
    """
    
    def __init__(self):
        pass
    
    async def update_credentials(self, client_id: str, client_secret: str) -> Dict:
        """
        Mettre à jour les credentials YouTube
        
        Args:
            client_id: Client ID YouTube
            client_secret: Client Secret YouTube
            
        Returns:
            dict: Confirmation de mise à jour
        """
        try:
            config_collection = get_config_collection()
            
            await config_collection.update_one(
                {"type": "youtube"},
                {
                    "$set": {
                        "type": "youtube",
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "is_authenticated": False
                    }
                },
                upsert=True
            )
            
            print(f"✅ YouTube credentials updated")
            
            return {
                "success": True,
                "message": "YouTube credentials updated"
            }
            
        except Exception as e:
            print(f"❌ Error updating YouTube credentials: {str(e)}")
            traceback.print_exc()
            raise
    
    async def get_stats(self) -> Dict:
        """
        Récupérer les statistiques d'utilisation YouTube
        
        Returns:
            dict: Statistiques YouTube
        """
        try:
            videos_collection = get_videos_collection()
            config_collection = get_config_collection()
            
            # Vérifier si YouTube est authentifié
            youtube_config = await config_collection.find_one({"type": "youtube"})
            is_authenticated = youtube_config and youtube_config.get("is_authenticated", False)
            
            # Compter les vidéos uploadées aujourd'hui
            today_start = start_of_day_utc()
            uploads_today = await videos_collection.count_documents({
                "uploaded_at": {"$gte": today_start}
            })
            
            # Compter total de vidéos uploadées
            total_uploads = await videos_collection.count_documents({
                "youtube_video_id": {"$exists": True, "$ne": None}
            })
            
            # Compter vidéos en attente d'upload
            pending_uploads = await videos_collection.count_documents({
                "youtube_video_id": {"$exists": False}
            })
            
            return {
                "authenticated": is_authenticated,
                "uploads_today": uploads_today,
                "total_uploads": total_uploads,
                "pending_uploads": pending_uploads,
                "quota_info": {
                    "daily_limit": 6,
                    "note": "YouTube API quota: 10,000 unités/jour. Upload = ~1600 unités"
                }
            }
            
        except Exception as e:
            print(f"❌ Error fetching YouTube stats: {str(e)}")
            traceback.print_exc()
            raise
