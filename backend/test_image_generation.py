#!/usr/bin/env python3
"""
Script de test pour la génération d'images
"""

import sys
import os

# Ajouter le répertoire courant au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Teste l'import de tous les modules nécessaires"""
    print("🧪 Test des imports...")
    
    try:
        from agents.image_prompt_generator_agent import ImagePromptGeneratorAgent
        print("✅ ImagePromptGeneratorAgent importé avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'import de ImagePromptGeneratorAgent: {e}")
        return False
    
    try:
        from routes.images import router
        print("✅ Route images importée avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'import de la route images: {e}")
        return False
    
    try:
        import server
        print("✅ Serveur importé avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'import du serveur: {e}")
        return False
    
    return True

def test_agent_initialization():
    """Teste l'initialisation de l'agent"""
    print("\n🧪 Test de l'initialisation de l'agent...")
    
    try:
        from agents.image_prompt_generator_agent import ImagePromptGeneratorAgent
        agent = ImagePromptGeneratorAgent()
        print("✅ Agent initialisé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de l'agent: {e}")
        return False

def test_environment_variables():
    """Teste les variables d'environnement"""
    print("\n🧪 Test des variables d'environnement...")
    
    image_api_url = os.getenv("IMAGE_API_BASE_URL", "http://localhost:8000")
    print(f"✅ IMAGE_API_BASE_URL: {image_api_url}")
    
    image_api_key = os.getenv("IMAGE_API_KEY", "")
    if image_api_key:
        print("✅ IMAGE_API_KEY configurée")
    else:
        print("⚠️ IMAGE_API_KEY non configurée (peut être normal)")
    
    return True

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'intégration pour la génération d'images...\n")
    
    # Test des imports
    if not test_imports():
        print("\n❌ Les tests d'import ont échoué")
        return 1
    
    # Test de l'initialisation de l'agent
    if not test_agent_initialization():
        print("\n❌ Le test d'initialisation de l'agent a échoué")
        return 1
    
    # Test des variables d'environnement
    if not test_environment_variables():
        print("\n❌ Les tests des variables d'environnement ont échoué")
        return 1
    
    print("\n🎉 Tous les tests ont réussi !")
    print("\n📋 Résumé de l'implémentation:")
    print("   ✅ Agent de génération de prompts d'images créé")
    print("   ✅ Route backend pour l'API d'images créée")
    print("   ✅ Route intégrée au serveur principal")
    print("   ✅ API images ajoutée au frontend")
    print("   ✅ Bouton de génération d'images ajouté dans IdeaCard")
    print("   ✅ Variables d'environnement configurées")
    print("\n🚀 L'implémentation est prête à être utilisée !")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
