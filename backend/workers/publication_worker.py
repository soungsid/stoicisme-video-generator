#!/usr/bin/env python
"""
Worker de publication automatique des vidéos YouTube

Ce worker:
- Vérifie la queue de vidéos planifiées toutes les 60 secondes
- Publie automatiquement les vidéos dont l'heure est arrivée
- Peut être démarré/arrêté via l'API
- Tourne en arrière-plan avec supervisor
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from database import connect_to_mongo
from services.publication_service import PublicationService

# Interval de vérification (en secondes)
CHECK_INTERVAL = 60

class PublicationWorker:
    """
    Worker qui tourne en boucle pour publier les vidéos planifiées
    """
    
    def __init__(self):
        self.publication_service = PublicationService()
        self.is_running = False
    
    async def start(self):
        """
        Démarrer le worker
        """
        print("="*60)
        print("🚀 PUBLICATION WORKER STARTED")
        print("="*60)
        print(f"Check interval: {CHECK_INTERVAL} seconds")
        print(f"Current time: {datetime.now().isoformat()}")
        print(f"Timezone: {os.getenv('TZ', 'UTC')}")
        print("="*60)
        
        # Connexion à MongoDB
        await connect_to_mongo()
        
        self.is_running = True
        self.publication_service.is_running = True
        
        # Boucle principale
        iteration = 0
        while self.is_running:
            try:
                iteration += 1
                current_time = datetime.now()
                
                print(f"\n[{iteration}] 🔍 Vérification de la queue - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Traiter la queue
                result = await self.publication_service.process_queue()
                
                if result['processed'] > 0:
                    print(f"✅ {result['successful']} vidéos publiées avec succès")
                    if result['failed'] > 0:
                        print(f"❌ {result['failed']} vidéos en erreur")
                else:
                    print("💤 Aucune vidéo à publier")
                
                # Attendre avant la prochaine vérification
                print(f"⏰ Prochaine vérification dans {CHECK_INTERVAL} secondes...")
                await asyncio.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n⚠️  Arrêt demandé par l'utilisateur")
                break
            except Exception as e:
                print(f"\n❌ Erreur dans le worker: {str(e)}")
                import traceback
                traceback.print_exc()
                # Attendre un peu avant de réessayer
                await asyncio.sleep(10)
        
        self.is_running = False
        self.publication_service.is_running = False
        print("\n🛑 PUBLICATION WORKER STOPPED")
    
    async def stop(self):
        """
        Arrêter le worker
        """
        print("⚠️  Arrêt du worker demandé...")
        self.is_running = False

if __name__ == "__main__":
    worker = PublicationWorker()
    
    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        print("\n⚠️  Worker arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
