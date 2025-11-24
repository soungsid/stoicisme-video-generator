"""
Worker de traitement des jobs de génération vidéo
S'exécute en continu et traite les jobs de la queue
"""
import asyncio
import sys
import os


# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import traceback

# Charger les variables d'environnement
load_dotenv()

# Import après load_dotenv
from models import IdeaStatus
from services.queue_service import QueueService
from agents.script_adapter_agent import ScriptAdapterAgent
from services.audio_service import AudioService
from services.video_service import VideoService


class VideoWorker:
    """Worker qui traite les jobs de génération vidéo"""
    
    def __init__(self):
        self.queue_service = None
        self.db = None
        self.db_client = None
        self.running = False
        self.poll_interval = 5  # Vérifier la queue toutes les 5 secondes
    
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
            print(f"✅ Worker connected to MongoDB: {db_name}")
        except Exception as e:
            print(f"❌ Worker MongoDB connection failed: {e}")
            raise
    
    async def update_idea_status(self, idea_id: str, status: IdeaStatus, error: str = None):
        """Mettre à jour le statut d'une idée"""
        ideas_collection = self.db.ideas
        update_data = {"status": status}
        if error:
            update_data["error_message"] = error
        
        await ideas_collection.update_one(
            {"id": idea_id},
            {"$set": update_data}
        )

    def determine_start_step(self, idea):
        """Déterminer l'étape de démarrage en fonction du statut actuel de l'idée."""
        status_to_step = {
            IdeaStatus.PENDING: "script",
            IdeaStatus.QUEUED: "script",
            IdeaStatus.SCRIPT_GENERATING: "script",
            IdeaStatus.SCRIPT_GENERATED: "audio",
            IdeaStatus.AUDIO_GENERATING: "audio",
            IdeaStatus.AUDIO_GENERATED: "video",
            IdeaStatus.VIDEO_GENERATING: "video",
            IdeaStatus.VIDEO_GENERATED: None,  # Terminé
        }
        
        current_status = IdeaStatus(idea.get("status"))
        next_step = status_to_step.get(current_status)
        
        if next_step:
            print(f"📍 Reprise à partir du statut '{current_status.value}' → Démarrage à '{next_step}'")
        return next_step
    
    async def process_job(self, job):
        """Traiter un job de génération vidéo"""
        idea_id = job.idea_id
        start_from = job.start_from
        
        print(f"🎬 Starting job {job.job_id} for idea {idea_id} (start_from: {start_from})")
        
        try:
            ideas_collection = self.db.ideas
            scripts_collection = self.db.scripts
            
            # Récupérer l'idée
            idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
            if not idea:
                raise Exception(f"Idea {idea_id} not found")
            
            # Déterminer l'étape de démarrage (reprise intelligente)
            start_step = self.determine_start_step(idea)
            
            if not start_step:
                print(f"✅ Idea {idea_id} already completed.")
                await self.queue_service.complete_job(job.job_id)
                return

            script_id = None
            
            # Étape 1: Générer le script
            if start_step == "script":
                print(f"📝 Generating script for idea {idea_id}")
                await self.update_idea_status(idea_id, IdeaStatus.SCRIPT_GENERATING)
                await self.script_service.generate_script(idea_id)
                # Le statut est mis à jour dans script_service
            
            # Récupérer le script_id pour les étapes suivantes
            script = await scripts_collection.find_one({"idea_id": idea_id}, {"_id": 0})
            if not script:
                raise Exception(f"Script for idea {idea_id} not found after generation step")
            script_id = script["id"]

            # Étape 2: Adapter le script et Générer l'audio
            if start_step in ["script", "audio"]:
                print(f"🔊 Generating audio for idea {idea_id}")
                await self.update_idea_status(idea_id, IdeaStatus.AUDIO_GENERATING)
                
                # Adapter le script
                adapter = ScriptAdapterAgent()
                adapted_script, phrases = await adapter.adapt_script(script["original_script"])
                await scripts_collection.update_one(
                    {"id": script_id},
                    {"$set": {
                        "elevenlabs_adapted_script": adapted_script,
                        "phrases": phrases
                    }}
                )
                
                # Générer l'audio avec concaténation et timestamps
                audio_service = AudioService()
                audio_generation = await audio_service.complete_audio_generation_with_timestamps(script_id)
                await self.update_idea_status(idea_id, IdeaStatus.AUDIO_GENERATED)

            # Étape 3: Générer la vidéo
            if start_step in ["script", "audio", "video"]:
                print(f"🎥 Generating video for idea {idea_id}")
                await self.update_idea_status(idea_id, IdeaStatus.VIDEO_GENERATING)
                video_service = VideoService()
                await video_service.generate_video(script_id=script_id)
                await self.update_idea_status(idea_id, IdeaStatus.VIDEO_GENERATED)
            
            # Job complété avec succès
            await self.queue_service.complete_job(job.job_id)
            print(f"✅ Job {job.job_id} completed successfully")
            
        except Exception as e:
            error_msg = f"{str(e)}\\n{traceback.format_exc()}"
            print(f"❌ Job {job.job_id} failed: {error_msg}")
            
            # Mettre à jour l'idée avec l'erreur
            await self.update_idea_status(idea_id, IdeaStatus.ERROR, error_msg[:1000])
            
            # Marquer le job comme échoué
            await self.queue_service.fail_job(job.job_id, error_msg[:500])
    
    async def run(self):
        """Boucle principale du worker"""
        print("🚀 Video Worker started")
        print(f"📊 Max concurrent jobs: {self.queue_service.max_concurrent}")
        
        self.running = True
        
        while self.running:
            try:
                # Vérifier si on peut traiter plus de jobs
                if await self.queue_service.can_process_more():
                    # Récupérer le prochain job
                    job = await self.queue_service.get_next_job()
                    
                    if job:
                        print(f"📥 Processing job: {job.job_id}")
                        await self.process_job(job)
                    else:
                        # Pas de job disponible, attendre
                        await asyncio.sleep(self.poll_interval)
                else:
                    # Limite atteinte, attendre
                    stats = await self.queue_service.get_queue_stats()
                    print(f"⏳ Max concurrent jobs reached ({stats['processing']}/{stats['max_concurrent']}). Waiting...")
                    await asyncio.sleep(self.poll_interval)
                    
            except Exception as e:
                print(f"❌ Worker error: {e}")
                traceback.print_exc()
                await asyncio.sleep(self.poll_interval)
    
    async def start(self):
        from services.script_service import ScriptService

        """Démarrer le worker"""
        await self.connect_to_mongo()
        
        # Initialiser le service de queue avec la connexion DB
        # On doit patcher les fonctions get_*_collection pour utiliser notre db
        import database
        database.db = self.db
        database.db_client = self.db_client
        
        self.queue_service = QueueService()
        self.script_service = ScriptService()
        
        await self.run()
    
    async def stop(self):
        """Arrêter le worker"""
        print("� Stopping worker...")
        self.running = False
        if self.db_client:
            self.db_client.close()

async def main():
    """Point d'entrée du worker"""
    worker = VideoWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        print("\\n🛑 Worker interrupted by user")
        await worker.stop()
    except Exception as e:
        print(f"❌ Worker crashed: {e}")
        traceback.print_exc()
        await worker.stop()

if __name__ == "__main__":
    asyncio.run(main())
