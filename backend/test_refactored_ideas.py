"""
Script de test pour le service de génération d'idées refactorisé
"""

import asyncio
import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.idea_management_service import IdeaManagementService
from models import IdeaGenerationRequest, VideoType


async def test_refactored_service():
    """Test du service refactorisé"""
    print('🧪 Test du service de génération d\'idées refactorisé...')
    
    service = IdeaManagementService()
    
    # Test 1: Génération avec count = 1 (cas normal)
    print('\n📝 Test 1: count = 1')
    request1 = IdeaGenerationRequest(
        count=1,
        video_type=VideoType.SHORT,
        duration_seconds=30
    )
    
    try:
        result1 = await service.create_ideas(request1)
        print(f'✅ Résultat: {result1["count"]} idée(s) générée(s)')
        for idea in result1['ideas']:
            print(f'   - {idea["title"]}')
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
        result2 = await service.create_ideas(request2)
        print(f'✅ Résultat: {result2["count"]} idée(s) générée(s)')
        for idea in result2['ideas']:
            print(f'   - {idea["title"]}')
            print(f'     Mots-clés: {idea["keywords"]}')
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
        result3 = await service.create_ideas(request3)
        print(f'✅ Résultat: {result3["count"]} idée(s) générée(s)')
        for idea in result3['ideas']:
            print(f'   - {idea["title"]}')
    except Exception as e:
        print(f'❌ Erreur: {e}')
    
    print('\n🎉 Tests terminés!')


if __name__ == "__main__":
    asyncio.run(test_refactored_service())
