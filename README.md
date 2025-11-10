# 📺 YouTube Channel Manager

Application web complète pour gérer votre chaîne YouTube : authentification OAuth, upload, modification, planification et publication automatique de vidéos.

## ⚡ Démarrage Rapide

### Option 1: Docker (Recommandé) 🐳

```bash
# 1. Cloner et configurer
git clone <votre-repo>
cd youtube-manager
cp backend/.env.example backend/.env
# Éditez backend/.env avec vos credentials

# 2. Démarrer
docker-compose up -d

# 3. Accéder
# Frontend: http://localhost:3000
# API: http://localhost:8001
# Docs: http://localhost:8001/docs
```

### Option 2: Développement Local 💻

```bash
# Installation
make install

# Démarrage
make dev

# Ou manuellement avec le script
./scripts/start.sh
```

## 📋 Configuration Requise

### 1. Google Cloud Platform

Créez un projet et configurez l'OAuth YouTube:

1. Allez sur [console.cloud.google.com](https://console.cloud.google.com)
2. Créez un projet: "YouTube Video Manager"
3. Activez "YouTube Data API v3"
4. Configurez l'écran de consentement OAuth
5. Créez des identifiants OAuth (Application Web)

**Scopes nécessaires**:
- `youtube.upload`
- `youtube.readonly`
- `youtube.force-ssl`

📖 **Guide complet**: [README_SETUP_GOOGLE.md](./README_SETUP_GOOGLE.md)

### 2. MongoDB

Obtenez une connexion MongoDB Atlas ou utilisez une instance locale.

### 3. Fichier .env

Créez `backend/.env`:

```env
# MongoDB
MONGO_USERNAME=your-username
MONGO_PASSWORD=your-password
MONGO_CLUSTER=cluster0.xxxxx.mongodb.net
DB_NAME=youtube_manager_db

# YouTube OAuth
YOUTUBE_CLIENT_ID=your-client-id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-xxxxx
YOUTUBE_REDIRECT_URI=http://localhost:8001/api/youtube/oauth/callback

# Timezone (UTC par défaut)
TZ=UTC
```

## 🎯 Fonctionnalités

- ✅ **Authentification YouTube OAuth 2.0**
- ✅ **Informations de chaîne** (abonnés, vues, statistiques)
- ✅ **Upload de vidéos** avec métadonnées
- ✅ **Modification de vidéos** (titre, description, tags)
- ✅ **Planification individuelle** avec date/heure
- ✅ **Planification en masse** avec configuration horaire
- ✅ **Publication automatique** via worker
- ✅ **Recherche et filtrage** de vidéos
- ✅ **Pagination** personnalisable

## 📚 Documentation

- **[README_COMPLETE.md](./README_COMPLETE.md)** - Documentation technique complète
- **[README_SETUP_GOOGLE.md](./README_SETUP_GOOGLE.md)** - Configuration Google Cloud étape par étape
- **[API Docs](http://localhost:8001/docs)** - Documentation interactive (après démarrage)

## 🔧 Commandes Utiles

### Avec Make

```bash
make install          # Installer les dépendances
make dev             # Démarrer en développement
make docker-up       # Démarrer avec Docker
make docker-logs     # Voir les logs Docker
make queue-status    # Statut de la queue
make queue-process   # Traiter la queue manuellement
make test            # Lancer les tests
make clean           # Nettoyer
```

### Docker

```bash
docker-compose up -d              # Démarrer
docker-compose logs -f            # Logs
docker-compose restart backend    # Redémarrer un service
docker-compose down              # Arrêter
```

### Supervisor (en local)

```bash
sudo supervisorctl status                   # État des services
sudo supervisorctl restart backend         # Redémarrer backend
sudo supervisorctl restart publication-worker  # Redémarrer worker
sudo supervisorctl logs backend tail       # Voir les logs
```

## 🐛 Debug

### VSCode

Fichiers de configuration déjà créés dans `.vscode/`:
- `launch.json` - Configurations de debug
- `settings.json` - Paramètres

**Utilisation**:
1. Ouvrir le projet dans VSCode
2. F5 → Choisir "Python: FastAPI Backend"
3. Placer des breakpoints et debugger

### IntelliJ / PyCharm

Créez une configuration Run/Debug:
```
Module name: uvicorn
Parameters: server:app --host 0.0.0.0 --port 8001 --reload
Working directory: /app/backend
```

📖 **Guide complet**: [README_COMPLETE.md#debug](./README_COMPLETE.md#-debug-vscode)

## 📊 API Endpoints

### Authentification
- `GET /api/youtube/auth/url` - URL OAuth
- `GET /api/youtube/config` - Statut authentification
- `POST /api/youtube/disconnect` - Déconnexion

### Vidéos
- `POST /api/youtube/upload/{video_id}` - Upload
- `PATCH /api/youtube/update/{youtube_video_id}` - Modification
- `GET /api/youtube/channel-info` - Infos chaîne

### Planification
- `POST /api/youtube/schedule/{video_id}` - Planifier une vidéo
- `POST /api/youtube/schedule/bulk` - Planification en masse
- `DELETE /api/youtube/schedule/{video_id}` - Annuler

### Queue
- `GET /api/youtube/queue/status` - Statut
- `POST /api/youtube/queue/process` - Traiter manuellement
- `GET /api/youtube/queue/scheduled-videos` - Vidéos planifiées

## 🕐 Gestion des Fuseaux Horaires

**Par défaut**: Toutes les dates sont en **UTC**.

Pour programmer en heure locale:
```javascript
// Frontend
const localDate = new Date('2025-11-10T09:00:00');
const isoDate = localDate.toISOString(); // Converti en UTC
```

Pour planification en masse:
```json
{
  "start_date": "2025-11-10",
  "publish_times": ["09:00", "18:00"]
  // ⚠️ Ces heures sont en UTC
}
```

📖 **Plus de détails**: [README_COMPLETE.md#gestion-des-fuseaux-horaires](./README_COMPLETE.md#-gestion-des-fuseaux-horaires)

## 🔍 Dépannage

### Backend ne démarre pas
```bash
tail -f /var/log/supervisor/backend.err.log
sudo supervisorctl restart backend
```

### Worker ne publie pas
```bash
# Vérifier le worker
sudo supervisorctl status publication-worker

# Traiter manuellement
curl -X POST http://localhost:8001/api/youtube/queue/process
```

### OAuth: invalid_client
Vérifiez que l'URI de redirection est exactement:
`http://localhost:8001/api/youtube/oauth/callback`

📖 **Guide complet**: [README_COMPLETE.md#dépannage](./README_COMPLETE.md#-dépannage)

## 🏗️ Architecture

```
├── backend/           # FastAPI (Python)
│   ├── routes/       # Endpoints API
│   ├── services/     # Logique métier
│   ├── workers/      # Workers asynchrones
│   └── server.py     # Application principale
├── frontend/         # React
├── docker-compose.yml
└── .vscode/         # Config debug
```

## 📝 Scripts

- **[start.sh](./scripts/start.sh)** - Démarrage rapide
- **[health-check.sh](./scripts/health-check.sh)** - Vérification santé

## 🎉 C'est Prêt!

Votre application est maintenant prête. Suivez ces étapes:

1. ✅ Configurez Google Cloud Platform
2. ✅ Remplissez le fichier `.env`
3. ✅ Démarrez l'application (`docker-compose up -d` ou `make dev`)
4. ✅ Ouvrez http://localhost:3000
5. ✅ Connectez votre compte YouTube
6. ✅ Gérez vos vidéos!

## 📄 Licence

MIT License

## 🤝 Support

- Documentation complète: [README_COMPLETE.md](./README_COMPLETE.md)
- Configuration Google Cloud: [README_SETUP_GOOGLE.md](./README_SETUP_GOOGLE.md)
- API Interactive: http://localhost:8001/docs

---

**Bon développement!** 🚀
