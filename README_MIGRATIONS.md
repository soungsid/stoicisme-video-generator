# Endpoints de Migration et Statistiques

Ce document décrit les nouveaux endpoints ajoutés pour gérer les migrations de base de données et récupérer les statistiques.

## Endpoints Disponibles

### 1. Exécuter les migrations
**POST** `/api/migrations/run`

Exécute toutes les migrations disponibles et retourne les résultats avec les statistiques mises à jour.

**Réponse:**
```json
{
  "success": true,
  "migrations": [
    {
      "name": "migrate_idea_statuses",
      "status": "completed",
      "description": "Migration des anciens statuts vers le nouveau système"
    },
    {
      "name": "migrate_new_status_and_script_id",
      "status": "completed", 
      "description": "Ajout des nouveaux statuts et du champ script_id"
    }
  ],
  "statistics": {
    "ideas": {
      "total": 150,
      "with_script": 120,
      "without_script": 30,
      "script_coverage_percentage": 80.0,
      "status_distribution": {
        "pending": 50,
        "queued": 20,
        "script_generated": 70,
        "video_generated": 10
      }
    },
    "scripts": {
      "total": 120,
      "status_distribution": {
        "generated": 100,
        "adapted": 20
      }
    },
    "videos": {
      "total": 10,
      "status_distribution": {
        "generated": 8,
        "published": 2
      }
    },
    "summary": {
      "total_items": 280,
      "completion_rate": 80.0
    }
  }
}
```

### 2. Récupérer les statistiques
**GET** `/api/migrations/statistics`

Retourne les statistiques actuelles de la base de données sans exécuter de migrations.

**Réponse:**
```json
{
  "success": true,
  "statistics": {
    "ideas": {
      "total": 150,
      "with_script": 120,
      "without_script": 30,
      "script_coverage_percentage": 80.0,
      "status_distribution": {
        "pending": 50,
        "queued": 20,
        "script_generated": 70,
        "video_generated": 10
      }
    },
    "scripts": {
      "total": 120,
      "status_distribution": {
        "generated": 100,
        "adapted": 20
      }
    },
    "videos": {
      "total": 10,
      "status_distribution": {
        "generated": 8,
        "published": 2
      }
    },
    "summary": {
      "total_items": 280,
      "completion_rate": 80.0
    }
  }
}
```

## Migrations Disponibles

### 1. `migrate_idea_statuses`
- **Description**: Met à jour les anciens statuts des idées vers le nouveau système de statuts simplifié
- **Mapping des statuts**:
  - `processing` → `queued`
  - `script_generating` → `queued`
  - `script_adapting` → `script_generated`
  - `script_adapted` → `script_generated`
  - `audio_generating` → `script_generated`
  - `video_generating` → `audio_generated`
  - `uploaded` → `video_generated`
  - `validated` → `pending`
  - `rejected` → `pending`

### 2. `migrate_new_status_and_script_id`
- **Description**: Ajoute les nouveaux statuts et le champ `script_id` aux idées
- **Fonctionnalités**:
  - Ajoute `script_id` aux idées qui ont un script associé
  - Vérifie la validité des statuts existants
  - Fournit des statistiques de distribution des statuts
  - Identifie les incohérences (idées avec script mais mauvais statut)

## Utilisation

### Via l'API REST
```bash
# Récupérer les statistiques
curl -X GET "http://localhost:8001/api/migrations/statistics"

# Exécuter les migrations
curl -X POST "http://localhost:8001/api/migrations/run"
```

### Via Python
```python
import httpx
import asyncio

async def run_migrations():
    async with httpx.AsyncClient() as client:
        # Récupérer les statistiques
        response = await client.get("http://localhost:8001/api/migrations/statistics")
        print(response.json())
        
        # Exécuter les migrations
        response = await client.post("http://localhost:8001/api/migrations/run")
        print(response.json())

asyncio.run(run_migrations())
```

### Via le script de test
```bash
python test_migration_endpoint.py
```

## Statistiques Disponibles

### Idées
- **total**: Nombre total d'idées
- **with_script**: Idées avec un script associé
- **without_script**: Idées sans script
- **script_coverage_percentage**: Pourcentage d'idées avec script
- **status_distribution**: Distribution par statut

### Scripts
- **total**: Nombre total de scripts
- **status_distribution**: Distribution par statut

### Vidéos
- **total**: Nombre total de vidéos
- **status_distribution**: Distribution par statut

### Résumé
- **total_items**: Total de tous les éléments
- **completion_rate**: Taux de complétion global

## Notes Importantes

1. Les migrations sont idempotentes et peuvent être exécutées plusieurs fois sans effet secondaire
2. Les statistiques sont calculées en temps réel à partir de la base de données
3. Les endpoints nécessitent que le serveur backend soit en cours d'exécution
4. Les migrations peuvent prendre quelques secondes selon la taille de la base de données
