# 📺 YouTube Channel Manager - Application Complète

Cette application permet de gérer complètement une chaîne YouTube.

## 🎯 Fonctionnalités

- ✅ Authentification YouTube OAuth
- ✅ Upload et modification de vidéos
- ✅ Planification automatique
- ✅ Queue de publication

## 📋 Configuration Google Cloud Platform

### Étape 1: Créer un Projet

1. Accédez à [https://console.cloud.google.com](https://console.cloud.google.com)
2. Créez un nouveau projet: "YouTube Video Manager"
3. Activez YouTube Data API v3

### Étape 2: Écran de Consentement OAuth

1. Type: Externe
2. Scopes requis:
   - youtube.upload
   - youtube.readonly
   - youtube.force-ssl

### Étape 3: Créer des Identifiants

1. Type: Application Web
2. URI de redirection: http://localhost:8001/api/youtube/oauth/callback

Voir le fichier complet pour plus de détails.
