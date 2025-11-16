"""
Test simplifié du service de génération d'idées refactorisé (sans base de données)
"""

import asyncio
import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.idea_management_service import IdeaManagementService
from models import IdeaGenerationRequest, VideoType


async def test_refactored_service_simple():
    """Test du service refactorisé sans sauvegarde en base"""
    print('🧪 Test simplifié du service de génération d\'idées refactorisé...')
    
    service = IdeaManagementService()
    
    # Test 1: Génération avec count = 1 (cas normal)
    print('\n📝 Test 1: count = 1')
    request1 = IdeaGenerationRequest(
        count=1,
        video_type=VideoType.SHORT,
        duration_seconds=30
    )
    
    try:
        # Test direct de la génération sans sauvegarde
        ideas = []
        previously_generated_titles = []
        idea = await service.generer_une_idee(request1, previously_generated_titles)
        ideas.append(idea)
        print(f'✅ Idée générée: {idea.title}')
        print(f'   Mots-clés: {idea.keywords}')
        print(f'   Type vidéo: {idea.video_type}')
        print(f'   Durée: {idea.duration_seconds}s')
    except Exception as e:
        print(f'❌ Erreur: {e}')
    
    # Test 2: Génération avec mots-clés
    print('\n📝 Test 2: avec mots-clés')
    request2 = IdeaGenerationRequest(
        count=2,
        keywords=['stoïcisme', 'sagesse'],
        video_type=VideoType.NORMAL,
        duration_seconds=60,
        sections_count=3
    )
    
    try:
        ideas = []
        previously_generated_titles = []
        for i in range(request2.count):
            idea = await service.generer_une_idee(request2, previously_generated_titles)
            ideas.append(idea)
            previously_generated_titles.append(idea.title)
            print(f'✅ Idée {i+1}/{request2.count}: {idea.title}')
            print(f'   Mots-clés: {idea.keywords}')
        
        # Test génération des sections
        if request2.video_type.value == "normal" and request2.sections_count:
            await service._generate_section_titles(ideas, request2.sections_count)
            for idea in ideas:
                print(f'   Sections: {idea.section_titles}')
    except Exception as e:
        print(f'❌ Erreur: {e}')
    
    # Test 3: Génération avec titre personnalisé
    print('\n📝 Test 3: avec titre personnalisé')
    request3 = IdeaGenerationRequest(
        count=1,
        custom_title="5 Habitudes stoïques pour une vie meilleure",
        video_type=VideoType.SHORT,
        duration_seconds=30
    )
    
    try:
        ideas = []
        previously_generated_titles = []
        idea = await service.generer_une_idee(request3, previously_generated_titles)
        ideas.append(idea)
        print(f'✅ Idée générée: {idea.title}')
        print(f'   Type: {idea.video_type}')
        print(f'   Durée: {idea.duration_seconds}s')
    except Exception as e:
        print(f'❌ Erreur: {e}')
    
    print('\n🎉 Tests simplifiés terminés!')


if __name__ == "__main__":
    asyncio.run(test_refactored_service_simple())
