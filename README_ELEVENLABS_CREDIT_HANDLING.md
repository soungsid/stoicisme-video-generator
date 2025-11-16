# Gestion des Crédits ElevenLabs

## Fonctionnalités Implémentées

### 1. Vérification des Crédits
- **Détection automatique** des erreurs liées aux crédits épuisés
- **Analyse des messages d'erreur** pour identifier les problèmes de limites de caractères
- **Rotation intelligente** entre les 5 clés API disponibles

### 2. Gestion des Erreurs
- **Décodage des erreurs** ElevenLabs pour identifier les problèmes de crédits
- **Messages d'erreur spécifiques** pour faciliter le débogage
- **Gestion différenciée** entre erreurs de crédits et autres erreurs

### 3. Suivi des Clés Épuisées
- **Liste des clés épuisées** maintenue en mémoire
- **Exclusion automatique** des clés épuisées de la rotation
- **Nettoyage quotidien** de la liste des clés épuisées

### 4. Logs Détaillés
- **Suivi en temps réel** de l'utilisation des clés
- **Statistiques** sur les clés disponibles vs épuisées
- **Analyse des erreurs** avec messages explicites

## Comment Ça Fonctionne

### Détection des Erreurs de Crédits
Le système analyse les messages d'erreur ElevenLabs pour détecter les indicateurs suivants :
- `insufficient credits`
- `not enough credits` 
- `quota exceeded`
- `character limit`
- `monthly character limit`
- `usage limit`
- `limit exceeded`

### Rotation des Clés
1. Le service charge les 5 clés API depuis les variables d'environnement
2. À chaque requête, il utilise la prochaine clé disponible
3. Si une clé est épuisée, elle est automatiquement exclue de la rotation
4. Le système continue avec les clés restantes

### Nettoyage Quotidien
- La liste des clés épuisées est **vidée automatiquement toutes les 24 heures**
- Cela permet de réutiliser les clés après le renouvellement mensuel des quotas

## Variables d'Environnement Requises

```bash
# Clés API ElevenLabs (5 maximum)
ELEVENLABS_API_KEY1=sk_...
ELEVENLABS_API_KEY2=sk_...
ELEVENLABS_API_KEY3=sk_...
ELEVENLABS_API_KEY4=sk_...
ELEVENLABS_API_KEY5=sk_...

# Voice ID (optionnel, valeur par défaut fournie)
ELEVENLABS_VOICE_ID=t8BrjWUT5Z23DLLBzbuY
```

## Exemple de Logs

```
✅ Loaded 5 ElevenLabs API keys
🔑 Using ElevenLabs key #2/5 (total: 5, exhausted: 0)
🎵 Generating audio test.mp3 for text: Ceci est un test...
✅ Audio generated successfully. Next step: saving audio
✅ Generated audio: test.mp3 (2038ms)

🔍 Analyzing ElevenLabs error: insufficient credits for this request
💳 Credit limit detected for API key: sk_9240ea1...
⚠️  Marked API key as exhausted: sk_9240ea1...
```

## Gestion des Cas d'Erreur

### Toutes les Clés Épuisées
Si toutes les clés API sont épuisées, le système lève une exception :
```
All ElevenLabs API keys are exhausted. Please add new keys or wait for daily reset.
```

### Autres Erreurs
Les erreurs non liées aux crédits (authentification, réseau, etc.) sont propagées normalement.

## Tests

Un script de test est disponible : `test_elevenlabs_credit_handling.py`

```bash
python test_elevenlabs_credit_handling.py
```

Ce script vérifie :
- La rotation des clés
- La détection des erreurs de crédits
- La gestion des clés épuisées
- La génération d'audio avec gestion d'erreurs

## Avantages

1. **Économie de Coûts** : Évite d'utiliser des clés épuisées
2. **Continuité de Service** : Rotation automatique entre clés disponibles
3. **Maintenance Automatique** : Nettoyage quotidien sans intervention
4. **Débogage Facile** : Logs détaillés pour le suivi des problèmes
5. **Évolutivité** : Facile d'ajouter de nouvelles clés API
