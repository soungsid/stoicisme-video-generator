import os
import requests

# Récupérer la clé d'API depuis la variable d'environnement
api_key = os.getenv("ELEVENLABS_API_KEY2")

if not api_key:
    raise ValueError("La clé d'API n'est pas définie dans la variable ELEVENLABS_API_KEY1")

# URL de l'API ElevenLabs pour la liste des modèles
url = "https://api.elevenlabs.io/v1/models"

# Requête GET
response = requests.get(url, headers={"xi-api-key": api_key})

if response.status_code == 200:
    models = response.json()
    for model in models:
        print(f"Nom : {model['name']}")
        print(f"ID : {model['model_id']}")
        print(f"Description : {model.get('description', 'Aucune description')}")
        print("-" * 40)
else:
    print(f"Erreur : {response.status_code} - {response.text}")
