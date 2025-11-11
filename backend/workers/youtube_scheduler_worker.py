"""
Worker de planification et publication automatique YouTube
Vérifie périodiquement les vidéos planifiées et les publie
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import datetime, timezone
import traceback

load_dotenv()

from services.youtube_service import YouTubeService
from agents.youtube_description_agent import YouTubeDescriptionAgent

class YouTubeSchedulerWorker:
    """Worker qui publie automatiquement les vidéos planifiées"""
    
    def __init__(self):
        self.db = None
        self.db_client = None
        self.running = False
        self.check_interval = 60  # Vérifier toutes les 60 secondes
    
    async def connect_to_mongo(self):
        """Connexion à MongoDB"""
        username = os.getenv("MONGO_USERNAME")
        password = os.getenv("MONGO_PASSWORD")
        cluster = os.getenv("MONGO_CLUSTER")
        app_name = os.getenv("MONGO_APP_NAME")
        db_name = os.getenv("DB_NAME", "interview_video_generator")
        
        connection_string = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName={app_name}"
        
        try:
            self.db_client = AsyncIOMotorClient(connection_string, server_api=ServerApi('1'))
            self.db = self.db_client[db_name]
            await self.db_client.admin.command('ping')
            print(f"✅ YouTube Scheduler connected to MongoDB: {db_name}")
        except Exception as e:
            print(f"❌ YouTube Scheduler MongoDB connection failed: {e}")
            raise
    
    async def process_scheduled_videos(self):
        """Traiter les vidéos dont la date de publication est arrivée"""
        try:
            videos_collection = self.db.videos
            scripts_collection = self.db.scripts
            ideas_collection = self.db.ideas
            
            # Trouver les vidéos planifiées dont la date est passée
            now = datetime.now(timezone.utc)
            print(f"process_scheduled_videos lancé à {now}" )
            scheduled_videos = await videos_collection.find({
                "is_scheduled": True,
                "$or": [
                    {"youtube_video_id": {"$exists": False}},  # champ inexistant
                    {"youtube_video_id": None},                # champ nul
                    {"youtube_video_id": ""}                   # champ vide
                ],
                "scheduled_publish_date": {"$lte": now}
            }).to_list(length=100)
            
            if not scheduled_videos:
                print("Aucune video planifié")
                return
            
            print(f"📅 {len(scheduled_videos)} vidéo(s) à publier")
            
            youtube_service = YouTubeService()
            description_agent = YouTubeDescriptionAgent()
            
            for video in scheduled_videos:
                try:
                    print(f"🎬 Publication de: {video['title']}")
                    
                    # Récupérer le script pour générer la description
                    script = await scripts_collection.find_one({"id": video["script_id"]}, {"_id": 0})
                    
                    # Générer une description YouTube optimisée
                    description = await description_agent.generate_description(
                        title=video["title"],
                        script=script.get("original_script", "") if script else "",
                        keywords=script.get("keywords", []) if script else []
                    )
                    
                    # Uploader sur YouTube
                    youtube_video_id, youtube_url = await youtube_service.upload_video(
                        video_relative_path=video["video_relative_path"],
                        title=video["title"],
                        description=description,
                        tags=script.get("keywords", []) if script else ["stoicisme", "philosophie"],
                        category_id="22"
                    )
                    
                    # Mettre à jour la vidéo
                    await videos_collection.update_one(
                        {"id": video["id"]},
                        {
                            "$set": {
                                "youtube_video_id": youtube_video_id,
                                "youtube_url": youtube_url,
                                "uploaded_at": datetime.now(timezone.utc),
                                "is_scheduled": False
                            }
                        }
                    )
                    
                    # Mettre à jour l'idée
                    from models import IdeaStatus
                    await ideas_collection.update_one(
                        {"id": video["idea_id"]},
                        {"$set": {"status": IdeaStatus.UPLOADED}}
                    )
                    
                    print(f"✅ Vidéo publiée: {youtube_url}")
                    
                except Exception as e:
                    print(f"❌ Erreur lors de la publication de {video['id']}: {e}")
                    traceback.print_exc()
                    
                    # Désactiver la planification en cas d'erreur
                    await videos_collection.update_one(
                        {"id": video["id"]},
                        {"$set": {"is_scheduled": False}}
                    )
        
        except Exception as e:
            print(f"❌ Erreur dans process_scheduled_videos: {e}")
            traceback.print_exc()
    
    async def run(self):
        """Boucle principale du scheduler"""
        print("🚀 YouTube Scheduler Worker started")
        print(f"⏰ Checking every {self.check_interval} seconds")
        
        self.running = True
        
        while self.running:
            try:
                await self.process_scheduled_videos()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                traceback.print_exc()
                await asyncio.sleep(self.check_interval)
    
    async def start(self):
        """Démarrer le scheduler"""
        await self.connect_to_mongo()
        await self.run()
    
    async def stop(self):
        """Arrêter le scheduler"""
        print("🛑 Stopping YouTube Scheduler...")
        self.running = False
        if self.db_client:
            self.db_client.close()

async def main():
    """Point d'entrée du scheduler"""
    scheduler = YouTubeSchedulerWorker()
    
    try:
        await scheduler.start()
    except KeyboardInterrupt:
        print("\\n🛑 Scheduler interrupted by user")
        await scheduler.stop()
    except Exception as e:
        print(f"❌ Scheduler crashed: {e}")
        traceback.print_exc()
        await scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
