# 🪟 Guide de Démarrage Windows

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

1. **Python 3.11+** : https://www.python.org/downloads/
   - ⚠️ Cochez "Add Python to PATH" lors de l'installation

2. **Node.js 18+** : https://nodejs.org/
   - Inclut automatiquement npm

3. **Git** (optionnel) : https://git-scm.com/

## 🚀 Démarrage Rapide

### Option 1 : Script Batch (.bat) - Simple

1. Double-cliquez sur `start_windows.bat`
2. Deux fenêtres s'ouvriront (Backend + Frontend)
3. Attendez que les serveurs démarrent (30-60 secondes)
4. Ouvrez http://localhost:3000 dans votre navigateur

### Option 2 : PowerShell (.ps1) - Recommandé

1. Clic droit sur `start_windows.ps1` → **Exécuter avec PowerShell**
2. Si erreur "script désactivé" :
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Relancez le script
4. Ouvrez http://localhost:3000

### Option 3 : Manuel

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
# ... jusqu'à KEY5
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

### "Erreur lors de l'installation des dépendances"
```cmd
# Backend
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Frontend
cd frontend
rd /s /q node_modules
npm cache clean --force
npm install
```

### Port déjà utilisé
```cmd
# Trouver et tuer le processus sur port 8001
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Trouver et tuer le processus sur port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## 📂 Structure des Fichiers Windows

```
C:\votre-projet\
├── backend\
│   ├── venv\              # Environnement virtuel Python
│   ├── server.py          # Serveur FastAPI
│   └── .env               # Configuration
├── frontend\
│   ├── node_modules\      # Dépendances Node.js
│   ├── src\               # Code React
│   └── package.json
├── start_windows.bat      # Script de démarrage
└── start_windows.ps1      # Script PowerShell
```

## 🔄 Arrêter les Serveurs

- **Avec scripts** : Fermez les fenêtres de terminal
- **Manuellement** : Appuyez sur `Ctrl + C` dans chaque terminal

## 📝 URLs Importantes

- Frontend : http://localhost:3000
- Backend API : http://localhost:8001
- Documentation API : http://localhost:8001/docs
- Health Check : http://localhost:8001/api/health

## 💡 Astuces Windows

1. **Ouvrir PowerShell en tant qu'Admin** :
   - Recherchez "PowerShell" → Clic droit → Exécuter en tant qu'administrateur

2. **Vérifier les versions** :
   ```cmd
   python --version
   node --version
   npm --version
   ```

3. **Variables d'environnement** :
   - Recherchez "Variables d'environnement"
   - Éditez "Path" pour ajouter Python/Node

## 🆘 Support

En cas de problème :
1. Vérifiez que Python et Node.js sont dans le PATH
2. Consultez les logs dans les fenêtres de terminal
3. Vérifiez `backend\.env` pour les configurations

---

**Bon développement ! 🎬**
