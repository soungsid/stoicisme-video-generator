"""
Script de test pour l'endpoint de migration
"""
import asyncio
import httpx
import sys
import os

# Ajouter le backend au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_migration_endpoints():
    """Tester les endpoints de migration"""
    base_url = "http://localhost:8001/api/migrations"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test de l'endpoint de statistiques
            print("📊 Test de l'endpoint /statistics...")
            response = await client.get(f"{base_url}/statistics")
            print(f"✅ GET /statistics - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Statistiques: {data}")
            else:
                print(f"   Erreur: {response.text}")
            
            # Test de l'endpoint de migration (POST)
            print("\n🔄 Test de l'endpoint /run...")
            response = await client.post(f"{base_url}/run")
            print(f"✅ POST /run - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Résultat migration: {data}")
            else:
                print(f"   Erreur: {response.text}")
                
        except httpx.ConnectError:
            print("❌ Impossible de se connecter au serveur. Assurez-vous que le serveur backend est en cours d'exécution.")
            print("   Commande pour démarrer le serveur: cd backend && python server.py")
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    print("🧪 Test des endpoints de migration...")
    asyncio.run(test_migration_endpoints())
