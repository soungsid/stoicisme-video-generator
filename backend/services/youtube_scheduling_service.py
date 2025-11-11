from datetime import datetime, timedelta
from typing import List, Dict
from database import get_videos_collection
from helpers.datetime_utils import parse_iso_date
import traceback

class YoutubeSchedulingService:
    """
    Service pour gérer la planification des vidéos YouTube
    """
    
    def __init__(self):
        pass
    
    async def schedule_video(self, video_id: str, publish_date: str) -> Dict:
        """
        Planifier la publication d'une vidéo
        
        Args:
            video_id: ID de la vidéo
            publish_date: Date de publication au format ISO
            
        Returns:
            Confirmation de planification avec la date programmée
        """
        try:
            videos_collection = get_videos_collection()
            
            # Vérifier que la vidéo existe
            video = await videos_collection.find_one({"id": video_id}, {"_id": 0})
            if not video:
                raise ValueError(f"Video {video_id} not found")
            
            # Parser la date
            scheduled_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            
            # Mettre à jour la vidéo
            result = await videos_collection.update_one(
                {"id": video_id},
                {
                    "$set": {
                        "scheduled_publish_date": scheduled_date,
                        "is_scheduled": True
                    }
                }
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Failed to update video {video_id}")
            
            print(f"✅ Video {video_id} scheduled for {scheduled_date.isoformat()}")
            
            return {
                "success": True,
                "video_id": video_id,
                "scheduled_date": scheduled_date.isoformat(),
                "timezone": "UTC"
            }
            
        except Exception as e:
            print(f"❌ Error scheduling video: {str(e)}")
            traceback.print_exc()
            raise
    
    async def unschedule_video(self, video_id: str) -> Dict:
        """
        Annuler la planification d'une vidéo
        
        Args:
            video_id: ID de la vidéo
            
        Returns:
            Confirmation d'annulation
        """
        try:
            videos_collection = get_videos_collection()
            
            # Vérifier que la vidéo existe
            video = await videos_collection.find_one({"id": video_id}, {"_id": 0})
            if not video:
                raise ValueError(f"Video {video_id} not found")
            
            result = await videos_collection.update_one(
                {"id": video_id},
                {
                    "$set": {
                        "is_scheduled": False
                    },
                    "$unset": {
                        "scheduled_publish_date": ""
                    }
                }
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Failed to update video {video_id}")
            
            print(f"✅ Video {video_id} unscheduled")
            
            return {
                "success": True,
                "video_id": video_id,
                "message": "Video unscheduled successfully"
            }
            
        except Exception as e:
            print(f"❌ Error unscheduling video: {str(e)}")
            traceback.print_exc()
            raise
    
    async def bulk_schedule(
        self, 
        start_date: str, 
        videos_per_day: int, 
        publish_times: List[str]
    ) -> Dict:
        """
        Planifier plusieurs vidéos en masse
        
        Args:
            start_date: Date de début (YYYY-MM-DD)
            videos_per_day: Nombre de vidéos par jour
            publish_times: Heures de publication (ex: ["09:00", "18:00"])
        
        Returns:
            Statistiques de planification
        """
        try:
            videos_collection = get_videos_collection()
            
            print("📅 Planification en masse démarrée")
            
            # Récupérer les vidéos non publiées
            unpublished_videos = await videos_collection.find({
                "$or": [
                    {"youtube_video_id": {"$exists": False}},
                    {"youtube_video_id": None}
                ]
            }).to_list(length=1000)
            
            print(f"{len(unpublished_videos)} videos non encore publiées")
            
            if not unpublished_videos:
                return {
                    "success": True,
                    "message": "No videos to schedule",
                    "scheduled_count": 0
                }
            
            # Parser la date de début
            current_date = datetime.fromisoformat(start_date)
            
            # Planifier les vidéos
            scheduled_count = 0
            time_index = 0
            
            for video in unpublished_videos:
                # Déterminer l'heure de publication (cycle à travers publish_times)
                publish_time = publish_times[time_index % len(publish_times)]
                hour, minute = map(int, publish_time.split(':'))
                
                # Créer la date complète avec l'heure
                scheduled_datetime = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                print(f"📌 Vidéo '{video.get('title', 'Sans titre')}' → {scheduled_datetime.isoformat()}")
                
                # Mettre à jour la vidéo
                await videos_collection.update_one(
                    {"id": video["id"]},
                    {
                        "$set": {
                            "scheduled_publish_date": scheduled_datetime,
                            "is_scheduled": True
                        }
                    }
                )
                
                scheduled_count += 1
                time_index += 1
                
                # Passer au jour suivant après avoir utilisé toutes les heures de publication
                if time_index % len(publish_times) == 0:
                    current_date += timedelta(days=1)
                    print(f"📆 Passage au jour suivant: {current_date.strftime('%Y-%m-%d')}")
            
            print(f"✅ {scheduled_count} vidéos planifiées avec succès")
            
            return {
                "success": True,
                "message": f"{scheduled_count} videos scheduled successfully",
                "scheduled_count": scheduled_count,
                "start_date": start_date,
                "timezone": "UTC"
            }
            
        except Exception as e:
            print(f"❌ Error in bulk scheduling: {str(e)}")
            traceback.print_exc()
            raise
