# Résumé des modifications - Fusion des routes /generate et /custom-script

## Objectif
Fusionner les routes `@router.post("/generate", response_model=dict)` et `@router.post("/custom-script", response_model=VideoIdea)` en créant un service dédié pour la logique de gestion des idées.

## Modifications apportées

### 1. Nouveau service dédié
**Fichier :** `backend/services/idea_management_service.py`

- Création de la classe `IdeaManagementService` qui centralise toute la logique de création d'idées
- Méthode `create_ideas()` pour gérer la génération d'idées automatiques, avec mots-clés ou avec titre personnalisé
- Méthode `create_custom_idea()` pour gérer la création d'idées avec script personnalisé
- Logique de génération de script pour les idées custom via `_generate_script_for_custom_idea()`

### 2. Mise à jour du modèle VideoIdea
**Fichier :** `backend/models.py`

- Ajout du champ `original_script: Optional[str]` pour stocker le script original des idées custom
- Ce champ permet de savoir si une idée est déjà scriptée

### 3. Refactoring des routes
**Fichier :** `backend/routes/ideas.py`

- Les routes `/generate` et `/custom-script` utilisent maintenant le nouveau service
- La logique métier est déléguée au service, les contrôleurs se contentent d'appeler le service
- Import du nouveau service `IdeaManagementService`

### 4. Fonctionnalités implémentées

#### Pour les idées custom :
- Si le type d'idée est "custom", après l'insertion de l'idée, le service de génération de script est appelé
- Vérification si un script existe déjà pour l'idée
- Mise à jour ou création du script selon le cas
- Stockage du script original dans le champ `original_script` de l'idée

#### Logique de génération de script :
- Vérification de l'existence d'un script pour l'idée
- Si script existe : mise à jour du script existant
- Si script n'existe pas : création d'un nouveau script
- Mise à jour du statut de l'idée en `SCRIPT_GENERATED`

## Avantages de cette refactorisation

1. **Séparation des préoccupations** : La logique métier est maintenant dans un service dédié
2. **Maintenabilité** : Les contrôleurs sont simplifiés et ne contiennent que la logique HTTP
3. **Réutilisabilité** : Le service peut être utilisé depuis d'autres parties de l'application
4. **Testabilité** : Le service peut être testé unitairement plus facilement
5. **Évolutivité** : Les nouvelles fonctionnalités peuvent être ajoutées au service sans modifier les contrôleurs

## Compatibilité

- **Frontend** : Aucune modification nécessaire, les routes API restent inchangées
- **Backend** : Toutes les fonctionnalités existantes sont préservées
- **Base de données** : Ajout d'un champ optionnel `original_script` dans le modèle VideoIdea

## Tests effectués

- Compilation du backend : ✅
- Compilation du service : ✅
- Compilation des routes : ✅
- Aucune erreur de syntaxe détectée

## Prochaines étapes

1. Tester les fonctionnalités avec des données réelles
2. Vérifier que la génération de script pour les idées custom fonctionne correctement
3. S'assurer que le champ `original_script` est correctement utilisé
4. Tester les différents modes de génération d'idées
