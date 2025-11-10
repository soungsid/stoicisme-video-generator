# 📺 YouTube Channel Manager - Documentation Complète

Application web complète pour gérer une chaîne YouTube : authentification, upload, modification, planification et publication automatique de vidéos.

---

## 📑 Table des Matières

1. [Fonctionnalités](#-fonctionnalités)
2. [Architecture](#-architecture)
3. [Installation](#-installation)
4. [Configuration Google Cloud](#-configuration-google-cloud-platform)
5. [Configuration .env](#-configuration-env)
6. [Docker](#-docker)
7. [Développement Local](#-développement-local)
8. [Debug VSCode](#-debug-vscode)
9. [Debug IntelliJ](#-debug-intellij)
10. [Worker de Publication](#-worker-de-publication)
11. [API Documentation](#-api-documentation)
12. [Gestion des Fuseaux Horaires](#-gestion-des-fuseaux-horaires)
13. [Dépannage](#-dépannage)

---

## 🎯 Fonctionnalités

### ✅ Authentification YouTube
- Connexion/déconnexion OAuth 2.0
- Gestion sécurisée des tokens
- Multi-comptes supportés

### ✅ Gestion de Chaîne
- Affichage des informations (nom, abonnés, vues, date création)
- Photo de profil
- Statistiques en temps réel

### ✅ Gestion des Vidéos
- Upload de nouvelles vidéos
- Modification des métadonnées (titre, description, tags)
- Suppression de vidéos
- Recherche et filtrage
- Tri personnalisé
- Pagination configurable

### ✅ Planification
- Planification individuelle avec date/heure précise
- Planification en masse avec configuration horaire
- Queue de publication automatique
- Support des fuseaux horaires

### ✅ Base de Données
- MongoDB pour le stockage
- Synchronisation automatique
- Historique complet des opérations

---

## 🏗️ Architecture

```
youtube-manager/
├── backend/                # API FastAPI (Python)
│   ├── routes/            # Endpoints API
│   ├── services/          # Logique métier
│   ├── workers/           # Workers asynchrones
│   ├── database.py        # Connexion MongoDB
│   ├── models.py          # Modèles Pydantic
│   └── server.py          # Application principale
├── frontend/              # Interface React
│   ├── src/
│   ├── public/
│   └── nginx.conf         # Config nginx pour Docker
├── ressources/            # Fichiers vidéos
├── docker-compose.yml     # Orchestration Docker
└── .vscode/              # Configuration debug
```

### Services Docker

1. **backend**: API FastAPI (port 8001)
2. **frontend**: Interface React (port 3000)
3. **publication-worker**: Worker de publication automatique
4. **mongodb**: Base de données (optionnel si MongoDB Atlas)

---

## 🚀 Installation

### Prérequis

- Python 3.11+
- Node.js 18+
- MongoDB (Atlas ou local)
- Docker & Docker Compose (optionnel)
- Compte Google Cloud Platform

### Installation Rapide

```bash
# Cloner le repository
git clone <votre-repo>
cd youtube-manager

# Configurer le .env
cp backend/.env.example backend/.env
# Éditez backend/.env avec vos credentials

# Option 1: Docker (recommandé)
docker-compose up -d

# Option 2: Développement local
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend (nouveau terminal)
cd frontend
yarn install
yarn start
```

---

## 📋 Configuration Google Cloud Platform

### Étape 1: Créer un Projet

1. Accédez à [console.cloud.google.com](https://console.cloud.google.com)
2. Cliquez sur le sélecteur de projet en haut
3. "NOUVEAU PROJET"
4. Nom: `YouTube Video Manager`
5. Cliquez sur "CRÉER"

### Étape 2: Activer YouTube Data API v3

1. Menu → "APIs et services" → "Bibliothèque"
2. Recherchez "YouTube Data API v3"
3. Cliquez sur "ACTIVER"

### Étape 3: Écran de Consentement OAuth

1. Menu → "APIs et services" → "Écran de consentement OAuth"
2. **Type d'utilisateur**: Externe
3. **Informations sur l'application**:
   - Nom: YouTube Video Manager
   - Email d'assistance: votre-email@example.com
   - Domaines autorisés: `localhost`

4. **Champs d'application (IMPORTANT)**:
   
   Cliquez sur "AJOUTER OU SUPPRIMER DES CHAMPS D'APPLICATION" et cochez:
   
   ```
   ✅ https://www.googleapis.com/auth/youtube.upload
   ✅ https://www.googleapis.com/auth/youtube.readonly
   ✅ https://www.googleapis.com/auth/youtube.force-ssl
   ```

5. **Utilisateurs test**:
   - Ajoutez votre adresse email Google (celle de votre chaîne YouTube)

### Étape 4: Créer les Identifiants OAuth

1. Menu → "APIs et services" → "Identifiants"
2. "+ CRÉER DES IDENTIFIANTS" → "ID client OAuth"
3. **Configuration**:
   
   ```
   Type d'application: Application Web
   Nom: YouTube Manager Client
   
   Origines JavaScript autorisées:
   - http://localhost:3000
   - http://localhost:8001
   
   URI de redirection autorisés:
   - http://localhost:8001/api/youtube/oauth/callback
   ```

4. **Récupérer les credentials**:
   - Copiez le **Client ID** 
   - Copiez le **Client Secret**

### Étape 5: Quotas

Par défaut, YouTube Data API v3 offre:
- **10,000 unités/jour**
- 1 upload = ~1,600 unités
- 1 recherche = ~100 unités

Pour augmenter le quota, faites une demande dans la console Google Cloud.

---

## ⚙️ Configuration .env

Créez `/app/backend/.env`:

```env
# ========================================
# MONGODB
# ========================================
MONGO_USERNAME=votre-username
MONGO_PASSWORD=votre-password
MONGO_CLUSTER=cluster0.xxxxx.mongodb.net
MONGO_APP_NAME=Cluster0
DB_NAME=youtube_manager_db

# ========================================
# YOUTUBE OAUTH
# ========================================
YOUTUBE_CLIENT_ID=votre-client-id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-xxxxx
YOUTUBE_REDIRECT_URI=http://localhost:8001/api/youtube/oauth/callback

# ========================================
# FUSEAU HORAIRE
# ========================================
# UTC par défaut (recommandé)
TZ=UTC

# Pour un fuseau local:
# TZ=Europe/Paris
# TZ=America/New_York

# ========================================
# RESSOURCES
# ========================================
RESOURCES_DIR=/app/ressources
```

---

## 🐳 Docker

### Démarrage

```bash
# Build et démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend
docker-compose logs -f publication-worker

# Arrêter les services
docker-compose down

# Rebuild après modification
docker-compose up -d --build
```

### Services Disponibles

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **MongoDB**: localhost:27017 (si utilisé localement)

### Commandes Utiles

```bash
# Status des services
docker-compose ps

# Restart un service
docker-compose restart backend

# Voir les ressources utilisées
docker stats

# Entrer dans un conteneur
docker-compose exec backend bash
docker-compose exec publication-worker bash

# Supprimer tout (services + volumes)
docker-compose down -v
```

---

## 💻 Développement Local

### Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv

# Activer
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Démarrer le serveur
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend

```bash
cd frontend

# Installer les dépendances
yarn install

# Démarrer le serveur de dev
yarn start
```

### Worker de Publication

```bash
cd backend
source venv/bin/activate

# Démarrer le worker
python workers/publication_worker.py
```

---

## 🐛 Debug VSCode

### Configuration Automatique

Les fichiers suivants sont déjà créés:
- `.vscode/launch.json` - Configurations de debug
- `.vscode/settings.json` - Paramètres Python/JavaScript
- `.vscode/extensions.json` - Extensions recommandées

### Utilisation

1. **Ouvrir le projet** dans VSCode
2. **Installer les extensions recommandées** (popup automatique)
3. **Sélectionner l'interpréteur Python**:
   - Cmd/Ctrl + Shift + P
   - "Python: Select Interpreter"
   - Choisir `./backend/venv/bin/python`
4. **Placer des breakpoints** (clic à gauche des numéros de ligne)
5. **Lancer le debug**:
   - F5 ou Run → Start Debugging
   - Choisir "Python: FastAPI Backend"

### Configurations Disponibles

- **Python: FastAPI Backend** - Debug du serveur principal
- **Python: Publication Worker** - Debug du worker
- **Python: Current File** - Debug du fichier actuel

### Raccourcis Debug

- **F5**: Start Debugging
- **F9**: Toggle Breakpoint
- **F10**: Step Over
- **F11**: Step Into
- **Shift+F11**: Step Out
- **Shift+F5**: Stop Debugging

---

## 🐛 Debug IntelliJ / PyCharm

### Configuration Backend

1. **Run → Edit Configurations**
2. **"+" → Python**

```
Name: FastAPI Backend
Module name: uvicorn
Parameters: server:app --host 0.0.0.0 --port 8001 --reload
Working directory: /app/backend
Environment variables: PYTHONPATH=/app/backend
Python interpreter: /app/backend/venv/bin/python
```

### Configuration Worker

1. **Run → Edit Configurations**
2. **"+" → Python**

```
Name: Publication Worker
Script path: /app/backend/workers/publication_worker.py
Working directory: /app/backend
Environment variables: PYTHONPATH=/app/backend
Python interpreter: /app/backend/venv/bin/python
```

### Configuration Frontend (JavaScript)

1. **Run → Edit Configurations**
2. **"+" → JavaScript Debug**

```
Name: React Frontend
URL: http://localhost:3000
Browser: Chrome
```

Ensuite, démarrez le frontend en terminal (`yarn start`) et lancez cette configuration pour debugger le JS/React.

### Utilisation

1. **Placer des breakpoints** (Cmd/Ctrl + F8)
2. **Lancer en mode debug** (Cmd/Ctrl + D)
3. **Utiliser les contrôles**:
   - Step Over: F8
   - Step Into: F7
   - Step Out: Shift + F8
   - Resume: Cmd/Ctrl + Alt + R

---

## 🤖 Worker de Publication

### Fonctionnement

Le worker vérifie automatiquement la queue toutes les 60 secondes et publie les vidéos dont l'heure de publication est arrivée.

### Démarrage

```bash
# Avec supervisor (production)
sudo supervisorctl start publication-worker
sudo supervisorctl status publication-worker

# En développement (terminal)
cd backend
python workers/publication_worker.py
```

### Logs

```bash
# Logs du worker
tail -f /var/log/supervisor/publication-worker.out.log

# Logs d'erreur
tail -f /var/log/supervisor/publication-worker.err.log

# Avec Docker
docker-compose logs -f publication-worker
```

### API Endpoints

```bash
# Statut de la queue
curl http://localhost:8001/api/youtube/queue/status

# Traiter la queue manuellement
curl -X POST http://localhost:8001/api/youtube/queue/process

# Voir les vidéos planifiées
curl http://localhost:8001/api/youtube/queue/scheduled-videos

# Démarrer le worker (flag)
curl -X POST http://localhost:8001/api/youtube/queue/start

# Arrêter le worker (flag)
curl -X POST http://localhost:8001/api/youtube/queue/stop
```

---

## 📚 API Documentation

### Base URL

- Local: `http://localhost:8001`
- Documentation interactive: `http://localhost:8001/docs`

### Endpoints Principaux

#### Authentification
```bash
# Obtenir l'URL d'authentification
GET /api/youtube/auth/url

# Callback OAuth (automatique)
GET /api/youtube/oauth/callback?code=xxx

# Statut d'authentification
GET /api/youtube/config

# Déconnecter
POST /api/youtube/disconnect

# Nettoyer les tokens
POST /api/youtube/clear-tokens
```

#### Informations Chaîne
```bash
# Infos complètes
GET /api/youtube/channel-info
```

#### Gestion Vidéos
```bash
# Upload
POST /api/youtube/upload/{video_id}
Body: {"title": "...", "description": "...", "tags": [...]}

# Modifier
PATCH /api/youtube/update/{youtube_video_id}
Body: {"title": "...", "description": "...", "tags": [...]}
```

#### Planification
```bash
# Planifier une vidéo
POST /api/youtube/schedule/{video_id}
Body: {"publish_date": "2025-11-10T09:00:00Z"}

# Planification en masse
POST /api/youtube/schedule/bulk
Body: {
  "start_date": "2025-11-10",
  "videos_per_day": 2,
  "publish_times": ["09:00", "18:00"]
}

# Annuler planification
DELETE /api/youtube/schedule/{video_id}
```

#### Queue de Publication
```bash
# Statut
GET /api/youtube/queue/status

# Traiter manuellement
POST /api/youtube/queue/process

# Vidéos planifiées
GET /api/youtube/queue/scheduled-videos

# Contrôle worker
POST /api/youtube/queue/start
POST /api/youtube/queue/stop
```

---

## 🕐 Gestion des Fuseaux Horaires

### Principe

Par défaut, **toutes les dates sont en UTC**.

### Configuration

```env
# Dans .env
TZ=UTC  # Recommandé
# ou
TZ=Europe/Paris
TZ=America/New_York
```

### Frontend → Backend

```javascript
// Convertir heure locale en UTC
const localDate = new Date('2025-11-10T09:00:00');
const isoDate = localDate.toISOString(); // "2025-11-10T08:00:00.000Z"

// Envoyer au backend
await fetch('/api/youtube/schedule/123', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ publish_date: isoDate })
});
```

### Backend → Frontend

```javascript
// Afficher en heure locale
const apiResponse = { scheduled_date: "2025-11-10T08:00:00Z" };
const date = new Date(apiResponse.scheduled_date);

// Format local
console.log(date.toLocaleString('fr-FR', { 
  timeZone: 'Europe/Paris' 
}));
// "10/11/2025, 09:00:00"
```

### Planification en Masse

Les heures dans `publish_times` sont **toujours UTC**:

```json
{
  "start_date": "2025-11-10",
  "publish_times": ["09:00", "18:00"]
}
```

Si vous êtes à Paris (UTC+1):
- 09:00 UTC = 10:00 Paris
- 18:00 UTC = 19:00 Paris

Pour programmer en heure locale, calculez l'offset:
```javascript
// Je veux 09:00 Paris (UTC+1)
const utcTime = "08:00"; // 09:00 - 1 heure
```

---

## 🔧 Dépannage

### Erreur OAuth: invalid_client

**Solution**:
1. Vérifiez que l'URI de redirection est exactement:
   `http://localhost:8001/api/youtube/oauth/callback`
2. Pas de slash final
3. Vérifiez les origines autorisées dans Google Console

### Erreur: quotaExceeded

**Solution**:
- Attendez minuit PST (reset quotidien)
- Demandez une augmentation dans Google Console
- Optimisez vos appels API

### Worker ne publie pas

**Solution**:
```bash
# Vérifier si le worker tourne
sudo supervisorctl status publication-worker

# Voir les logs
tail -f /var/log/supervisor/publication-worker.out.log

# Redémarrer
sudo supervisorctl restart publication-worker

# Traiter manuellement
curl -X POST http://localhost:8001/api/youtube/queue/process
```

### Vidéo publiée à la mauvaise heure

**Solution**:
- Vérifiez que les dates sont en UTC
- Ajoutez l'offset dans la date: `2025-11-10T09:00:00+01:00`
- Vérifiez `TZ` dans `.env`

### Backend ne démarre pas

**Solution**:
```bash
# Vérifier les logs
tail -f /var/log/supervisor/backend.err.log

# Vérifier MongoDB
curl http://localhost:8001/health

# Redémarrer
sudo supervisorctl restart backend
```

---

## 📝 Licence

MIT License

---

## 🎉 C'est Prêt!

Votre application de gestion YouTube est maintenant complètement configurée!

**Checklist finale**:
- ✅ Google Cloud Platform configuré
- ✅ Fichier .env rempli
- ✅ Docker ou environnement local prêt
- ✅ Worker de publication actif
- ✅ Configuration debug VSCode/IntelliJ

**Démarrage**:
```bash
# Avec Docker
docker-compose up -d

# Ou local
cd backend && uvicorn server:app --reload
cd frontend && yarn start
cd backend && python workers/publication_worker.py
```

**Accédez à l'application**: http://localhost:3000

Bon développement! 🚀
