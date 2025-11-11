import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
from database import get_videos_collection, get_config_collection
from services.youtube_service import YouTubeService
from helpers.datetime_utils import now_utc
import traceback

class PublicationService:
    """
    Service pour gérer la publication automatique des vidéos planifiées
    """
    
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.is_running = False
    
    async def get_scheduled_videos(self) -> List[Dict]:
        """
        Récupérer les vidéos planifiées dont l'heure est arrivée
        """
        videos_collection = get_videos_collection()
        current_time = datetime.now(timezone.utc)
        
        # Trouver les vidéos planifiées dont la date est passée
        scheduled_videos = await videos_collection.find({
                "is_scheduled": True,
                "$or": [
                    {"youtube_video_id": {"$exists": False}},  # champ inexistant
                    {"youtube_video_id": None},                # champ nul
                    {"youtube_video_id": ""}                   # champ vide
                ],
                "scheduled_publish_date": {"$lte": current_time}
            }).to_list(length=100)
        
        return scheduled_videos
    
    async def publish_video(self, video: Dict) -> Dict:
        """
        Publier une vidéo sur YouTube
        
        Args:
            video: Document de la vidéo à publier
            
        Returns:
            Résultat de la publication avec statut
        """
        try:
            print(f"📤 Publication de la vidéo: {video['title']}")
            
            # Uploader sur YouTube (le service gère tout automatiquement)
            result = await self.youtube_service.upload_video(
                video_id=video['id']
            )
            
            print(f"✅ Vidéo publiée: {result['youtube_url']}")
            
            return {
                "success": True,
                "video_id": video['id'],
                "youtube_video_id": result['youtube_video_id'],
                "youtube_url": result['youtube_url']
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la publication: {str(e)}")
            traceback.print_exc()
            
            # Marquer la vidéo comme ayant une erreur
            from database import get_videos_collection
            videos_collection = get_videos_collection()
            await videos_collection.update_one(
                {"id": video['id']},
                {
                    "$set": {
                        "publication_error": str(e),
                        "publication_error_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            return {
                "success": False,
                "video_id": video['id'],
                "error": str(e)
            }
    
    async def process_queue(self) -> Dict:
        """
        Traiter la queue de publication
        
        Returns:
            Statistiques de traitement
        """
        try:
            scheduled_videos = await self.get_scheduled_videos()
            
            if not scheduled_videos:
                return {
                    "processed": 0,
                    "successful": 0,
                    "failed": 0,
                    "message": "No videos to publish"
                }
            
            print(f"\n📊 {len(scheduled_videos)} vidéos à publier")
            
            results = {
                "processed": 0,
                "successful": 0,
                "failed": 0,
                "videos": []
            }
            
            for video in scheduled_videos:
                result = await self.publish_video(video)
                results["processed"] += 1
                
                if result["success"]:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                
                results["videos"].append(result)
                
                # Petite pause entre chaque publication
                await asyncio.sleep(2)
            
            print(f"\n✅ Publication terminée: {results['successful']}/{results['processed']} réussies\n")
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement de la queue: {str(e)}")
            traceback.print_exc()
            return {
                "processed": 0,
                "successful": 0,
                "failed": 0,
                "error": str(e)
            }
    
    async def get_queue_status(self) -> Dict:
        """
        Obtenir le statut actuel de la queue
        """
        videos_collection = get_videos_collection()
        current_time = datetime.now(timezone.utc)
        
        # Vidéos en attente
        pending_count = await videos_collection.count_documents({
            "is_scheduled": True,
            "youtube_video_id": {"$exists": False},
            "scheduled_publish_date": {"$lte": current_time}
        })
        
        # Vidéos planifiées (futures)
        future_count = await videos_collection.count_documents({
            "is_scheduled": True,
            "youtube_video_id": {"$exists": False},
            "scheduled_publish_date": {"$gt": current_time}
        })
        
        # Vidéos publiées
        published_count = await videos_collection.count_documents({
            "youtube_video_id": {"$exists": True}
        })
        
        # Vidéos avec erreur
        error_count = await videos_collection.count_documents({
            "publication_error": {"$exists": True}
        })
        
        return {
            "current_time": current_time.isoformat(),
            "worker_running": self.is_running,
            "pending_publication": pending_count,
            "scheduled_future": future_count,
            "published": published_count,
            "errors": error_count
        }
