# 🆕 Nouvelles Fonctionnalités - Guide Utilisateur

## 📝 Génération d'Idées - 3 Options

### Accès
Cliquez sur le bouton **"Générer"** en haut de la page Idées.

### Option 1 : Génération Automatique
**Quand l'utiliser ?** Laissez l'IA générer des idées optimisées automatiquement.

1. Cliquez sur l'onglet **"Génération auto"**
2. Choisissez le nombre d'idées (1-20)
3. Cliquez **"Générer"**

✅ Le système génère des titres accrocheurs + mots-clés SEO automatiquement.

### Option 2 : Avec Mots-Clés Spécifiques
**Quand l'utiliser ?** Vous voulez des idées sur un thème précis.

1. Cliquez sur l'onglet **"Avec mots-clés"**
2. Choisissez le nombre d'idées
3. Entrez vos mots-clés séparés par des virgules
   - Exemple: `Marc Aurèle, résilience, sagesse`
4. Cliquez **"Générer"**

✅ Le système génère des idées ciblées autour de vos mots-clés.

### Option 3 : Script Personnalisé
**Quand l'utiliser ?** Vous avez déjà écrit votre script.

1. Cliquez sur l'onglet **"Script custom"**
2. Collez votre script (minimum 50 caractères)
3. Choisissez le type : Short (9:16) ou Normal (16:9)
4. Définissez la durée en secondes
5. (Optionnel) Ajoutez des mots-clés
6. Cliquez **"Générer"**

✅ Le système génère un titre accrocheur automatiquement et crée l'idée directement avec statut "script_generated". Vous pouvez ensuite lancer l'adaptation → audio → vidéo.

## ✏️ Édition de Scripts

### Accès au Script
1. Cliquez sur une idée qui a un script généré
2. Vous verrez le statut "Script prêt" ou plus avancé
3. *(Feature à venir)* Cliquez sur "Voir détails" pour éditer

### Ce que vous pouvez modifier
- **Titre** : Change aussi le titre de l'idée
- **Script** : Le contenu du script
  - ⚠️ Si modifié, réinitialise l'adaptation et l'audio
- **Mots-clés** : Met à jour les mots-clés de l'idée

### API d'édition
```javascript
await scriptsApi.updateScript(scriptId, {
  title: 'Nouveau titre',
  original_script: 'Script modifié...',
  keywords: 'stoicisme,philosophie,sagesse'
});
```

## 🔔 Notifications Modernes

### Plus d'alert() ou confirm() !
Le système utilise maintenant des composants modernes :

**Toast (notifications)**
- Apparaissent en haut à droite
- 4 types : succès, erreur, warning, info
- Disparaissent automatiquement après 5 secondes
- Peuvent être fermées manuellement

**Modal de confirmation**
- Remplace les `window.confirm()`
- Plus clair et professionnel
- Mode danger (rouge) pour actions critiques

## 🔍 Recherche

La barre de recherche filtre en temps réel :
- Par **titre**
- Par **mots-clés**
- Par **statut**

Exemple: tapez "Marc" pour voir toutes les idées contenant Marc Aurèle.

## ☑️ Sélection Multiple

### Utilisation
1. Cochez plusieurs idées (checkbox à gauche de chaque carte)
2. OU cliquez "Tout sélectionner"
3. Cliquez sur **"Générer (X)"** en haut
4. Confirmez dans le modal

✅ Les pipelines se lancent séquentiellement.

## 📊 Barre de Progression

Chaque idée en cours de génération affiche :
- **Barre de progression** (0-100%)
- **Étape actuelle** : "Génération script...", "Audio en cours...", etc.
- **Pourcentage** en temps réel

Rafraîchissement automatique toutes les 3 secondes.

## 🔄 Reprise du Pipeline

Si une génération échoue ou s'arrête :
1. Un bouton apparaît selon l'étape
   - "Adapter" si script généré
   - "Audio" si script adapté
   - "Vidéo" si audio généré
   - "Réessayer" si erreur
2. Cliquez pour reprendre là où ça s'est arrêté

✅ Pas besoin de tout recommencer !

## 🎯 Workflow Complet

### Avec Script Auto
1. Cliquer **"Générer"** → Option 1 ou 2
2. Sélectionner une idée → **"Valider"**
3. Cliquer **"Générer"** sur l'idée
4. Suivre la progression automatiquement
5. Une fois terminé : **"Upload YouTube"**

### Avec Script Custom
1. Cliquer **"Générer"** → Option 3
2. Coller votre script
3. L'idée est créée avec statut "Script généré"
4. Cliquer **"Adapter"** pour continuer
5. Pipeline se poursuit normalement

## 🛠️ Commandes Utiles

### Redémarrer uniquement le backend

**Linux/Mac:**
```bash
./restart_backend.sh
```

**Windows:**
```cmd
restart_backend.bat
```

**Avec Supervisor:**
```bash
sudo supervisorctl restart backend
```

### Vérifier les logs
```bash
# Backend
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log

# Frontend
tail -f /var/log/supervisor/frontend.err.log
```

### Tester l'API
```bash
# Health check
curl http://localhost:8001/api/health

# Générer 2 idées
curl -X POST http://localhost:8001/api/ideas/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 2}'

# Générer avec keywords
curl -X POST http://localhost:8001/api/ideas/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 2, "keywords": ["stoicisme", "résilience"]}'

# Script custom
curl -X POST http://localhost:8001/api/ideas/custom-script \
  -H "Content-Type: application/json" \
  -d '{
    "script_text": "Votre long script ici...",
    "keywords": ["Marc Aurèle"],
    "video_type": "short",
    "duration_seconds": 30
  }'
```

## 💡 Astuces

1. **Mots-clés pertinents** : Utilisez des termes spécifiques pour des idées plus ciblées
2. **Script custom** : Idéal pour recycler du contenu existant
3. **Sélection multiple** : Générez plusieurs vidéos d'un coup pendant la nuit
4. **Recherche** : Retrouvez rapidement une idée par mot-clé ou statut
5. **Reprise** : Si erreur, pas de panique, reprenez où vous étiez

## 🐛 Problèmes Fréquents

### Le modal de génération ne s'ouvre pas
- Vérifiez que le frontend est bien démarré
- Rafraîchissez la page (F5)
- Regardez la console navigateur (F12)

### Toast n'apparaît pas
- Les toasts s'auto-ferment après 5 secondes
- Vérifiez qu'il n'y a pas d'erreur console

### Script custom rejeté
- Minimum 50 caractères requis
- Vérifiez que tous les champs sont remplis

### Pipeline bloqué
- Vérifiez les logs backend
- Utilisez le bouton de reprise approprié
- En dernier recours, redémarrez le backend

---

**Questions ? Consultez le README.md principal pour plus de détails !**
