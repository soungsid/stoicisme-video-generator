# 📋 Configuration Google Cloud Platform - Guide Complet

## Étape 1: Créer un Projet Google Cloud

1. **Accéder à la Console**
   - URL: https://console.cloud.google.com
   - Connectez-vous avec votre compte Google

2. **Créer le projet**
   - Cliquez sur le sélecteur de projet (en haut)
   - "NOUVEAU PROJET"
   - Nom: `YouTube Video Manager`
   - Cliquez "CRÉER"

## Étape 2: Activer YouTube Data API v3

1. Menu → "APIs et services" → "Bibliothèque"
2. Recherchez "YouTube Data API v3"
3. Cliquez "ACTIVER"

## Étape 3: Écran de Consentement OAuth

1. Menu → "APIs et services" → "Écran de consentement OAuth"
2. Type: **Externe**
3. Informations:
   - Nom: YouTube Video Manager
   - Email: votre-email@example.com
   - Domaines autorisés: localhost

4. **Champs d'application (IMPORTANT)**:
   ```
   ✅ https://www.googleapis.com/auth/youtube.upload
   ✅ https://www.googleapis.com/auth/youtube.readonly  
   ✅ https://www.googleapis.com/auth/youtube.force-ssl
   ```

5. Utilisateurs test:
   - Ajoutez votre email Google (celui de YouTube)

## Étape 4: Créer les Identifiants

1. Menu → "APIs et services" → "Identifiants"
2. "+ CRÉER DES IDENTIFIANTS" → "ID client OAuth"
3. Configuration:
   - Type: Application Web
   - Nom: YouTube Manager Client
   - Origines JavaScript: http://localhost:3000, http://localhost:8001
   - URI de redirection: **http://localhost:8001/api/youtube/oauth/callback**

4. Copiez:
   - Client ID
   - Client Secret

## Étape 5: Mettre à Jour .env

```env
YOUTUBE_CLIENT_ID=votre-client-id
YOUTUBE_CLIENT_SECRET=votre-client-secret
```

