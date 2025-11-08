# 🎬 Générateur Automatique de Vidéos YouTube - Stoïcisme

Système complet d'automatisation pour générer des vidéos YouTube sur le stoïcisme, de l'idée jusqu'à la publication.

## 📋 Fonctionnalités

### ✨ Pipeline Complet
1. **Génération d'idées** - AI génère des titres accrocheurs et SEO-friendly
2. **Création de scripts** - Scripts personnalisés adaptés à la durée choisie
3. **Adaptation ElevenLabs V3** - Injection automatique de marqueurs d'émotion
4. **Génération audio** - Synthèse vocale avec rotation de 5 comptes ElevenLabs
5. **Assemblage vidéo** - Combinaison audio + vidéo template + sous-titres
6. **Upload YouTube** - Publication automatique sur votre chaîne

### 🎯 Types de Vidéos
- **Shorts** (9:16) - Format vertical pour YouTube Shorts
- **Vidéos normales** (16:9) - Format horizontal classique
- Durée configurable de 10 à 600 secondes

## 🏗️ Architecture

```
/app/
├── backend/                 # API FastAPI
│   ├── server.py           # Point d'entrée
│   ├── database.py         # MongoDB Atlas
│   ├── models.py           # Modèles de données
│   ├── routes/             # Endpoints API
│   │   ├── ideas.py        # Gestion des idées
│   │   ├── scripts.py      # Génération de scripts
│   │   ├── audio.py        # Génération audio
│   │   ├── videos.py       # Assemblage vidéo
│   │   ├── youtube_routes.py  # Upload YouTube
│   │   └── config.py       # Configuration
│   ├── services/           # Services métier
│   │   ├── elevenlabs_service.py  # Rotation 5 clés API
│   │   ├── audio_service.py       # Gestion audio + timestamps
│   │   ├── video_service.py       # Assemblage vidéo
│   │   └── youtube_service.py     # Upload YouTube
│   └── agents/             # Agents IA
│       ├── idea_generator_agent.py     # Génération d'idées
│       ├── script_generator_agent.py   # Génération de scripts
│       └── script_adapter_agent.py     # Adaptation ElevenLabs
│
├── frontend/               # Interface React
│   └── src/
│       ├── pages/         # Pages principales
│       │   ├── IdeasPage.js      # Gestion des idées
│       │   ├── VideosPage.js     # Liste des vidéos
│       │   └── ConfigPage.js     # Configuration
│       └── components/    # Composants réutilisables
│
└── ressources/
    ├── video-template/    # 15 templates vidéo (1-15.mp4)
    └── videos/           # Vidéos générées (organisées par slug)
```

## 🚀 Démarrage Rapide

### Services
Les services sont gérés par Supervisor et démarrent automatiquement :

```bash
# Redémarrer tous les services
sudo supervisorctl restart all

# Vérifier le statut
sudo supervisorctl status

# Redémarrer individuellement
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# Script de redémarrage backend (Linux)
./restart_backend.sh

# Script de redémarrage backend (Windows)
restart_backend.bat
```

### URLs d'accès
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Documentation API**: http://localhost:8001/docs

## ⚙️ Configuration

### 1. Clés API ElevenLabs (OBLIGATOIRE)

Éditez `/app/backend/.env` et ajoutez vos 5 clés ElevenLabs :

```bash
ELEVENLABS_API_KEY1=sk_votre_cle_1
ELEVENLABS_API_KEY2=sk_votre_cle_2
ELEVENLABS_API_KEY3=sk_votre_cle_3
ELEVENLABS_API_KEY4=sk_votre_cle_4
ELEVENLABS_API_KEY5=sk_votre_cle_5
```

Le système fait une rotation automatique des clés pour économiser les quotas.

### 2. Configuration Voix (Optionnel)

Par défaut : Voix Austin (`Bj9UqZbhQsanLzgalpEG`)

Pour changer :
```bash
ELEVENLABS_VOICE_ID=votre_voice_id
ELEVENLABS_VOICE_NAME=NomDeLaVoix
```

### 3. YouTube API (Pour Upload)

1. Créez un projet Google Cloud
2. Activez YouTube Data API v3
3. Créez des credentials OAuth 2.0
4. Ajoutez dans `.env` :

```bash
YOUTUBE_CLIENT_ID=votre_client_id
YOUTUBE_CLIENT_SECRET=votre_client_secret
```

5. Authentifiez-vous via l'interface (page Configuration)

### 4. LLM (Configuré par défaut)

**DeepSeek** est configuré et prêt à l'emploi. Vous pouvez aussi utiliser OpenAI ou Gemini en modifiant `AI_PROVIDER` dans `.env`.

## 📖 Guide d'utilisation

### Workflow Complet

#### 1. Générer des Idées
1. Allez sur la page **Idées**
2. Cliquez sur **"Générer des idées"**
3. Choisissez le nombre d'idées (1-20)
4. L'IA génère des titres accrocheurs

#### 2. Valider une Idée
1. Cliquez sur **"Valider"** pour une idée
2. Choisissez :
   - Type : Short (9:16) ou Normal (16:9)
   - Durée : 10-600 secondes
   - Mots-clés SEO (optionnel)
3. Confirmez

#### 3. Générer la Vidéo
1. Cliquez sur **"Générer"** pour l'idée validée
2. Le pipeline complet s'exécute :
   - ✅ Génération du script (DeepSeek)
   - ✅ Adaptation ElevenLabs V3
   - ✅ Génération audio par phrases
   - ✅ Assemblage vidéo + audio + sous-titres
3. Patientez quelques minutes

#### 4. Upload YouTube
1. Allez sur la page **Vidéos**
2. Cliquez sur **"Upload YouTube"**
3. La vidéo est publiée sur votre chaîne

## 🎨 Templates Vidéo

15 templates disponibles dans `/app/ressources/video-template/` (1-15.mp4)

Le système sélectionne aléatoirement un template et le boucle automatiquement pour correspondre à la durée audio.

## 📁 Organisation des Fichiers

Chaque vidéo créée a son propre dossier :

```
/app/ressources/videos/
└── titre-de-la-video-en-slug/
    ├── audio/
    │   ├── phrase_000.mp3
    │   ├── phrase_001.mp3
    │   └── ...
    ├── combined_audio.mp3
    └── titre-de-la-video-en-slug.mp4
```

### 📂 Répertoire Ressources

Le répertoire `/app/ressources/` est configuré via la variable d'environnement `RESOURCES_DIR` dans `/app/backend/.env` et contient :

```
/app/ressources/
├── video-template/           # Templates vidéo de fond
│   ├── 1.mp4                # 15 vidéos template au format MP4
│   ├── 2.mp4
│   └── ... (jusqu'à 15.mp4)
│
└── videos/                   # Vidéos générées (organisées par slug)
    └── [slug-titre]/        # Un dossier par vidéo
        ├── audio/           # Fichiers audio par phrase
        │   ├── phrase_000.mp3
        │   ├── phrase_001.mp3
        │   └── ...
        ├── combined_audio.mp3  # Audio combiné final
        └── [slug-titre].mp4    # Vidéo finale
```

### 🌐 Accès aux Médias via API

Les vidéos et fichiers audio générés sont accessibles via l'endpoint `/media` :

**Format d'URL :**
```
http://localhost:8001/media/videos/{slug-titre}/{slug-titre}.mp4
http://localhost:8001/media/videos/{slug-titre}/audio/phrase_000.mp3
http://localhost:8001/media/videos/{slug-titre}/combined_audio.mp3
```

**Exemple :**
```bash
# Accéder à une vidéo générée
curl http://localhost:8001/media/videos/les-3-principes-du-stoicisme/les-3-principes-du-stoicisme.mp4

# Accéder à un fichier audio
curl http://localhost:8001/media/videos/les-3-principes-du-stoicisme/audio/phrase_000.mp3
```

**Configuration :**
- L'endpoint `/media` est configuré dans `/app/backend/server.py` 
- Sert les fichiers statiques depuis le répertoire défini par `RESOURCES_DIR`
- Les URLs sont automatiquement générées par `video_service.py` et `audio_service.py`
- Les chemins sont relatifs à `RESOURCES_DIR` pour une portabilité maximale

## 🔧 API REST

### Endpoints Principaux

#### Idées
```bash
POST   /api/ideas/generate              # Générer des idées
GET    /api/ideas/                      # Liste toutes les idées
PATCH  /api/ideas/{id}/validate         # Valider une idée
PATCH  /api/ideas/{id}/reject           # Rejeter une idée
```

#### Scripts
```bash
POST   /api/scripts/generate            # Générer un script
POST   /api/scripts/{id}/adapt          # Adapter pour ElevenLabs
GET    /api/scripts/by-idea/{idea_id}   # Script d'une idée
```

#### Audio
```bash
POST   /api/audio/generate/{script_id}  # Générer l'audio
GET    /api/audio/by-script/{script_id} # Info audio
```

#### Vidéos
```bash
POST   /api/videos/generate/{script_id} # Générer la vidéo
GET    /api/videos/                     # Liste des vidéos
GET    /api/videos/by-idea/{idea_id}    # Vidéo d'une idée
```

#### YouTube
```bash
GET    /api/youtube/auth/url            # URL d'authentification
POST   /api/youtube/upload/{video_id}   # Upload vidéo
GET    /api/youtube/config              # Statut auth
```

## 🤖 Agents IA

### IdeaGeneratorAgent
- Génère des titres accrocheurs
- Optimisation SEO
- Formules qui fonctionnent (hooks, curiosité)

### ScriptGeneratorAgent
- Scripts adaptés à la durée
- Structure optimisée (hook + contenu + CTA)
- Exemples du stoïcisme (Marc Aurèle, Sénèque, Épictète)

### ScriptAdapterAgent
- Injection de marqueurs ElevenLabs V3
- Émotions : [excited], [whispers], [sighs], [curious]
- Effets : [laughs], [applause], [clapping]
- Division intelligente en phrases

## 📊 Marqueurs ElevenLabs V3

### Émotions
- `[excited]` - Enthousiasme
- `[whispers]` - Chuchotement
- `[sighs]` - Soupir
- `[curious]` - Curiosité
- `[laughs]` - Rire
- `[sarcastic]` - Sarcasme

### Effets Sonores
- `[applause]` - Applaudissements
- `[clapping]` - Claquements
- `[explosion]` - Explosion
- `[gunshot]` - Coup de feu

## 🔄 Rotation des Clés ElevenLabs

Le système utilise automatiquement vos 5 clés ElevenLabs en rotation pour :
- Éviter les limites de quota
- Maximiser la production
- Pas de configuration manuelle nécessaire

## 🔧 Dépannage

### Backend ne démarre pas
```bash
# Vérifier les logs
tail -f /var/log/supervisor/backend.err.log

# Redémarrer avec le script
./restart_backend.sh

# OU manuellement
sudo supervisorctl restart backend
```

### Redémarrage rapide backend uniquement

**Linux/Mac:**
```bash
./restart_backend.sh
```

**Windows:**
```cmd
restart_backend.bat
```

**Ou avec supervisor:**
```bash
sudo supervisorctl restart backend
```

### Frontend ne compile pas
```bash
# Vérifier les logs
tail -f /var/log/supervisor/frontend.err.log

# Réinstaller les dépendances
cd /app/frontend && yarn install
sudo supervisorctl restart frontend
```

### MongoDB non connecté
```bash
# Vérifier les credentials dans .env
cat /app/backend/.env | grep MONGO

# Tester la connexion
curl http://localhost:8001/api/health
```

### ElevenLabs ne génère pas d'audio
```bash
# Vérifier les clés
curl http://localhost:8001/api/config/elevenlabs

# S'assurer qu'au moins une clé commence par "sk_"
```

## 📈 Statuts des Idées

- **pending** - En attente de validation
- **validated** - Validée, prête pour génération
- **script_generated** - Script créé
- **audio_generated** - Audio généré
- **video_generated** - Vidéo prête
- **uploaded** - Publiée sur YouTube
- **rejected** - Rejetée

## 💡 Bonnes Pratiques

1. **Templates vidéo** : Ajoutez vos propres templates dans `/app/ressources/video-template/`
2. **Durée optimale** :
   - Shorts : 30-60 secondes
   - Vidéos : 120-300 secondes
3. **Mots-clés** : Ajoutez 3-5 mots-clés SEO pertinents
4. **Quotas** : Surveillez vos quotas ElevenLabs et YouTube

## 🚨 Limites Actuelles

- Sous-titres : Implémentation basique (à améliorer avec ImageMagick)
- Templates : 15 templates fournis (ajoutez les vôtres)
- Langues : Optimisé pour le français

## 📝 Logs

```bash
# Backend
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Frontend
tail -f /var/log/supervisor/frontend.out.log
tail -f /var/log/supervisor/frontend.err.log
```

## 🎯 Prochaines Étapes

1. Configurez vos 5 clés ElevenLabs
2. (Optionnel) Configurez YouTube API pour l'upload
3. Générez vos premières idées
4. Validez et lancez la génération
5. Uploadez sur YouTube

## 🙏 Support

Pour toute question ou problème :
1. Consultez les logs
2. Vérifiez la configuration dans `.env`
3. Testez les endpoints API individuellement

---

**Note** : Ce système est conçu pour être évolutif. N'hésitez pas à ajouter vos propres templates vidéo et à personnaliser les prompts des agents IA selon vos besoins.
