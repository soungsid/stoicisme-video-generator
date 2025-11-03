# 🪟 Guide de Démarrage Windows

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

1. **Python 3.11+** : https://www.python.org/downloads/
   - ⚠️ Cochez "Add Python to PATH" lors de l'installation

2. **Node.js 18+** : https://nodejs.org/
   - Inclut automatiquement npm

## 🚀 Démarrage Rapide

### Simple : Double-clic sur le script

1. Double-cliquez sur `start_windows.bat`
2. Deux fenêtres s'ouvriront (Backend + Frontend)
3. Attendez que les serveurs démarrent (30-60 secondes)
4. Ouvrez http://localhost:3000 dans votre navigateur

### Manuel (si le script ne fonctionne pas)

#### Terminal 1 - Backend
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 2 - Frontend
```cmd
cd frontend
npm install
set PORT=3000
npm start
```

## 🔧 Configuration

### 1. ElevenLabs API Keys

Éditez `backend\.env` :
```env
ELEVENLABS_API_KEY1=sk_votre_cle_1
ELEVENLABS_API_KEY2=sk_votre_cle_2
```

### 2. YouTube API (Optionnel)

Éditez `backend\.env` :
```env
YOUTUBE_CLIENT_ID=votre_client_id
YOUTUBE_CLIENT_SECRET=votre_client_secret
```

## 🛠️ Dépannage

### "Python n'est pas reconnu..."
- Réinstallez Python et cochez "Add to PATH"
- Ou ajoutez manuellement : `C:\Python311` et `C:\Python311\Scripts`

### "npm n'est pas reconnu..."
- Réinstallez Node.js
- Redémarrez votre ordinateur après installation

### Port déjà utilisé
```cmd
# Trouver et tuer le processus sur port 8001
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

## 📝 URLs Importantes

- Frontend : http://localhost:3000
- Backend API : http://localhost:8001
- Documentation API : http://localhost:8001/docs

---

**Bon développement ! 🎬**
