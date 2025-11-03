# 🎬 Guide Rapide - Générateur de Vidéos YouTube Stoïcisme

## ✅ Statut Actuel

### Services en ligne ✓
- ✅ Backend API (FastAPI) : http://localhost:8001
- ✅ Frontend React : http://localhost:3000
- ✅ MongoDB Atlas : Connecté
- ✅ Documentation API : http://localhost:8001/docs

### Configuration actuelle
- ✅ DeepSeek : Configuré et fonctionnel
- ✅ MongoDB : Connecté à votre cluster Atlas
- ✅ ElevenLabs : 1 clé configurée sur 5
- ⚠️ YouTube : Non authentifié (voir instructions ci-dessous)

## 🚀 Prochaines Étapes

### 1. Configurer les 4 autres clés ElevenLabs (RECOMMANDÉ)

Pour maximiser la production et éviter les limites de quota :

```bash
# Éditez le fichier .env
nano /app/backend/.env

# Remplacez les lignes suivantes avec vos vraies clés :
ELEVENLABS_API_KEY2=sk_votre_cle_2
ELEVENLABS_API_KEY3=sk_votre_cle_3
ELEVENLABS_API_KEY4=sk_votre_cle_4
ELEVENLABS_API_KEY5=sk_votre_cle_5

# Redémarrez le backend
sudo supervisorctl restart backend
```

### 2. Configurer YouTube (OPTIONNEL - pour l'upload)

#### A. Créer les credentials Google Cloud

1. Allez sur https://console.cloud.google.com
2. Créez un nouveau projet ou sélectionnez-en un
3. Activez **YouTube Data API v3** :
   - Menu → APIs & Services → Library
   - Recherchez "YouTube Data API v3"
   - Cliquez "Enable"

4. Créez des credentials OAuth 2.0 :
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Type: Web application
   - Authorized redirect URIs: `http://localhost:8001/api/youtube/oauth/callback`
   - Notez le Client ID et Client Secret

#### B. Configurer dans l'application

```bash
# Éditez le fichier .env
nano /app/backend/.env

# Ajoutez vos credentials :
YOUTUBE_CLIENT_ID=votre_client_id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=votre_client_secret

# Redémarrez le backend
sudo supervisorctl restart backend
```

#### C. S'authentifier

1. Ouvrez http://localhost:3000
2. Allez dans Configuration
3. Cliquez "Authentifier avec YouTube"
4. Acceptez les permissions Google
5. Vous serez redirigé - l'authentification est complète !

## 🎬 Utilisation

### Workflow Complet

1. **Page Idées** (http://localhost:3000)
   - Cliquez "Générer des idées"
   - Entrez le nombre d'idées (ex: 5)
   - L'IA génère des titres accrocheurs

2. **Valider une idée**
   - Cliquez "Valider" sur l'idée qui vous plaît
   - Choisissez :
     * Type : Short (9:16) ou Normal (16:9)
     * Durée : 30s pour short, 120-180s pour normal
     * Mots-clés : stoicisme, philosophie, sagesse
   - Confirmez

3. **Générer la vidéo**
   - Cliquez "Générer" sur l'idée validée
   - Le pipeline complet s'exécute (3-5 minutes) :
     1. Génération du script
     2. Adaptation ElevenLabs V3
     3. Génération audio phrase par phrase
     4. Assemblage vidéo finale
   - Une alerte confirmera chaque étape

4. **Upload YouTube**
   - Allez dans "Vidéos"
   - Cliquez "Upload YouTube"
   - La vidéo est publiée !

## 🔍 Test Rapide

### Générer votre première idée

```bash
# Via API
curl -X POST http://localhost:8001/api/ideas/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 3}'

# Via Interface
# Ouvrez http://localhost:3000 et cliquez "Générer des idées"
```

### Vérifier la configuration

```bash
# ElevenLabs
curl http://localhost:8001/api/config/elevenlabs

# LLM
curl http://localhost:8001/api/config/llm

# YouTube
curl http://localhost:8001/api/config/youtube
```

## 📊 Monitoring

### Vérifier les services

```bash
# Statut général
sudo supervisorctl status

# Logs en temps réel
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.out.log
```

### Tester le backend

```bash
# Health check
curl http://localhost:8001/api/health

# Liste des idées
curl http://localhost:8001/api/ideas/

# Liste des vidéos
curl http://localhost:8001/api/videos/
```

## 💡 Exemples de Titres Générés

L'IA génère des titres optimisés comme :
- "Quand quelqu'un ne vous apprécie pas, faites CECI | Sagesse stoïque"
- "Ce secret stoïque les rendra obsédés par vous"
- "5 Habitudes terribles que vous ne devez absolument pas prendre!"
- "Comment le stoïcisme peut transformer votre vie en 30 jours"

## 📁 Structure des Vidéos

Chaque vidéo est organisée dans son propre dossier :

```
/app/ressources/videos/
└── quand-quelqu-un-ne-vous-apprecie-pas/
    ├── audio/
    │   ├── phrase_000.mp3
    │   ├── phrase_001.mp3
    │   └── ...
    ├── combined_audio.mp3
    └── quand-quelqu-un-ne-vous-apprecie-pas.mp4
```

## 🛠️ Commandes Utiles

```bash
# Redémarrer tous les services
sudo supervisorctl restart all

# Redémarrer seulement le backend
sudo supervisorctl restart backend

# Redémarrer seulement le frontend
sudo supervisorctl restart frontend

# Vérifier les logs backend
tail -f /var/log/supervisor/backend.err.log

# Vérifier les logs frontend
tail -f /var/log/supervisor/frontend.err.log

# Tester la connexion MongoDB
curl http://localhost:8001/api/health
```

## 🎯 Durées Recommandées

### Shorts (9:16)
- **Optimal** : 30-60 secondes
- **Maximum** : 90 secondes
- Format vertical, accrocheur

### Vidéos Normales (16:9)
- **Court** : 120-180 secondes (2-3 minutes)
- **Moyen** : 180-300 secondes (3-5 minutes)
- **Long** : 300-600 secondes (5-10 minutes)

## ❓ FAQ

### Combien de temps prend la génération d'une vidéo ?
- Script : 10-20 secondes
- Audio : 30-60 secondes (selon durée)
- Vidéo : 1-2 minutes
- **Total** : 3-5 minutes par vidéo

### Puis-je ajouter mes propres templates vidéo ?
Oui ! Ajoutez vos fichiers .mp4 dans `/app/ressources/video-template/`

### Combien de vidéos puis-je générer avec 1 clé ElevenLabs ?
Cela dépend de votre quota. C'est pourquoi on utilise 5 clés en rotation !

### Que faire si une génération échoue ?
1. Vérifiez les logs : `tail -f /var/log/supervisor/backend.err.log`
2. Vérifiez votre quota ElevenLabs
3. Relancez la génération

## 🚨 Troubleshooting

### "No valid ElevenLabs API keys found"
→ Vérifiez que vos clés commencent par "sk_" dans le .env

### "YouTube not authenticated"
→ Complétez la configuration YouTube (voir section 2 ci-dessus)

### "Error connecting to MongoDB"
→ Vérifiez vos credentials MongoDB Atlas dans le .env

### Backend ne démarre pas
```bash
sudo supervisorctl restart backend
tail -f /var/log/supervisor/backend.err.log
```

## 📞 Besoin d'aide ?

1. Consultez le README.md complet : `/app/README.md`
2. Vérifiez la documentation API : http://localhost:8001/docs
3. Examinez les logs pour les erreurs détaillées

---

**Prêt à commencer ?**

1. ✅ Services lancés
2. ⚠️ Ajoutez vos 4 autres clés ElevenLabs (recommandé)
3. ⚠️ Configurez YouTube si vous voulez uploader (optionnel)
4. 🎬 Ouvrez http://localhost:3000 et générez votre première vidéo !

**Bon courage avec vos vidéos sur le stoïcisme ! 🏛️**
