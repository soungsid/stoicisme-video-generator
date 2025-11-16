#!/usr/bin/env python3
"""
Script de test pour vérifier les modifications apportées à l'édition des entités
"""

import sys
import os

# Ajouter le chemin du backend
sys.path.append('backend')

try:
    # Test 1: Import des modèles
    from models import Script, VideoIdea
    print("✅ Modèles importés avec succès")
    
    # Test 2: Vérifier les champs du modèle Script
    script_fields = [field for field in Script.model_fields.keys()]
    print(f"✅ Champs du modèle Script: {script_fields}")
    
    # Vérifier que video_guideline est présent
    if 'video_guideline' in script_fields:
        print("✅ Champ video_guideline présent dans le modèle Script")
    else:
        print("❌ Champ video_guideline manquant dans le modèle Script")
    
    # Vérifier que youtube_description est présent
    if 'youtube_description' in script_fields:
        print("✅ Champ youtube_description présent dans le modèle Script")
    else:
        print("❌ Champ youtube_description manquant dans le modèle Script")
    
    # Test 3: Créer une instance de Script avec les nouveaux champs
    test_script = Script(
        idea_id="test-idea-id",
        title="Test Script",
        original_script="Ceci est un script de test",
        youtube_description="Description YouTube de test",
        video_guideline="Instructions spéciales pour le LLM"
    )
    print("✅ Instance de Script créée avec les nouveaux champs")
    
    # Test 4: Vérifier les champs du modèle VideoIdea
    idea_fields = [field for field in VideoIdea.model_fields.keys()]
    print(f"✅ Champs du modèle VideoIdea: {idea_fields}")
    
    # Vérifier que section_titles est présent
    if 'section_titles' in idea_fields:
        print("✅ Champ section_titles présent dans le modèle VideoIdea")
    else:
        print("❌ Champ section_titles manquant dans le modèle VideoIdea")
    
    # Test 5: Créer une instance de VideoIdea avec section_titles
    test_idea = VideoIdea(
        title="Test Idea",
        keywords=["test", "stoicisme"],
        video_type="short",
        duration_seconds=30,
        section_titles=["Introduction", "Développement", "Conclusion"]
    )
    print("✅ Instance de VideoIdea créée avec section_titles")
    
    print("\n🎉 Tous les tests de modèles ont réussi !")
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur lors du test: {e}")
    sys.exit(1)
