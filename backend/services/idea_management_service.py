"""
Service dédié à la gestion des idées de vidéos
Fusionne les fonctionnalités des routes /generate et /custom-script
"""

from typing import List, Dict, Optional
from fastapi import HTTPException, status
from models import VideoIdea, IdeaStatus, IdeaGenerationRequest, Script
from database import get_ideas_collection, get_scripts_collection
from agents.idea_generator_agent import IdeaGeneratorAgent
from agents.section_title_generator_agent import SectionTitleGeneratorAgent
from services.script_service import ScriptService
from datetime import datetime
import uuid


class IdeaManagementService:
    """
    Service pour gérer la création et la génération d'idées de vidéos
    """
    
    def __init__(self):
        self.idea_generator = IdeaGeneratorAgent()
        self.script_service = ScriptService()
    
    async def create_ideas(self, request: IdeaGenerationRequest) -> Dict:
        """
        Créer des idées de vidéos selon différents modes
        
        Args:
            request: Requête de génération d'idées
            
        Returns:
            dict: Résultat de la création avec les idées générées
        """
        try:
            ideas = []
            
            # Mode 1: Script personnalisé (une seule idée)
            if request.script_text:
                idea = await self._create_custom_script_idea(request)
                ideas = [idea]
                print(f"✨ Idée créée avec script personnalisé: {idea.title}")
            
            # Mode 2: Titre personnalisé (une seule idée)
            elif request.custom_title:
                idea = await self._create_custom_title_idea(request)
                ideas = [idea]
                print(f"✨ Idée créée avec titre personnalisé: {request.custom_title}")
            
            # Mode 3: Génération avec mots-clés
            elif request.keywords:
                ideas = await self._generate_ideas_with_keywords(request)
            
            # Mode 4: Génération automatique
            else:
                ideas = await self._generate_automatic_ideas(request)
            
            # Générer les titres de sections si nécessaire
            if request.video_type.value == "normal" and request.sections_count and request.sections_count > 0:
                await self._generate_section_titles(ideas, request.sections_count)
            
            # Sauvegarder en base de données
            ideas_dict = await self._save_ideas(ideas)
            
            return {
                "success": True,
                "count": len(ideas),
                "ideas": ideas_dict,
                "custom_title_used": bool(request.custom_title),
                "custom_script_used": bool(request.script_text)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating ideas: {str(e)}"
            )
    
    async def _create_custom_script_idea(self, request: IdeaGenerationRequest) -> VideoIdea:
        """Créer une idée avec un script personnalisé"""
        # Utiliser le titre fourni ou en générer un basé sur le script
        if request.custom_title:
            title = request.custom_title
            print(f"✨ Utilisation du titre personnalisé: {title}")
        else:
            title = await self.idea_generator.generate_title_from_script(
                request.script_text, 
                request.keywords or []
            )
            print(f"✨ Titre généré: {title}")
        
        # Créer l'idée (SANS sections car script custom)
        idea = VideoIdea(
            title=title,
            keywords=request.keywords or [],
            video_type=request.video_type,
            duration_seconds=request.duration_seconds,
            sections_count=None,  # Pas de sections pour script custom
            section_titles=None,  # Pas de sections pour script custom
            status=IdeaStatus.PENDING,  # On laisse en PENDING pour la génération de script
            original_script=request.script_text,  # Stocker le script original
            validated_at=datetime.now()
        )
        
        # Sauvegarder l'idée
        ideas_collection = get_ideas_collection()
        await ideas_collection.insert_one(idea.model_dump())
        
        # Générer le script via le service de script
        await self._generate_script_for_custom_idea(idea.id, request.script_text)
        
        # Récupérer l'idée mise à jour
        updated_idea = await ideas_collection.find_one({"id": idea.id}, {"_id": 0})
        
        return VideoIdea(**updated_idea)
    
    async def _create_custom_title_idea(self, request: IdeaGenerationRequest) -> VideoIdea:
        """Créer une idée avec un titre personnalisé"""
        idea = VideoIdea(
            title=request.custom_title,
            keywords=request.keywords or [],
            video_type=request.video_type,
            duration_seconds=request.duration_seconds,
            sections_count=request.sections_count if request.video_type.value == "normal" else None,
            status=IdeaStatus.PENDING
        )
        return idea
    
    async def _generate_ideas_with_keywords(self, request: IdeaGenerationRequest) -> List[VideoIdea]:
        """Générer des idées avec mots-clés"""
        ideas = await self.idea_generator.generate_ideas_with_keywords(
            count=request.count, 
            keywords=request.keywords
        )
        # Appliquer les paramètres aux idées générées
        for idea in ideas:
            idea.video_type = request.video_type
            idea.duration_seconds = request.duration_seconds
            if request.video_type.value == "normal" and request.sections_count:
                idea.sections_count = request.sections_count
        return ideas
    
    async def _generate_automatic_ideas(self, request: IdeaGenerationRequest) -> List[VideoIdea]:
        """Générer des idées automatiquement"""
        ideas = await self.idea_generator.generate_ideas(count=request.count)
        # Appliquer les paramètres aux idées générées
        for idea in ideas:
            idea.video_type = request.video_type
            idea.duration_seconds = request.duration_seconds
            if request.video_type.value == "normal" and request.sections_count:
                idea.sections_count = request.sections_count
        return ideas
    
    async def _generate_section_titles(self, ideas: List[VideoIdea], sections_count: int):
        """Générer les titres de sections pour les idées"""
        section_agent = SectionTitleGeneratorAgent()
        
        for idea in ideas:
            try:
                section_titles = await section_agent.generate_section_titles(
                    title=idea.title,
                    keywords=idea.keywords,
                    sections_count=sections_count
                )
                idea.section_titles = section_titles
                print(f"✅ Titres de sections générés pour: {idea.title}")
            except Exception as e:
                print(f"⚠️  Erreur génération sections pour {idea.title}: {e}")
                idea.section_titles = []
    
    async def _save_ideas(self, ideas: List[VideoIdea]) -> List[Dict]:
        """Sauvegarder les idées en base de données"""
        ideas_collection = get_ideas_collection()
        ideas_dict = [idea.model_dump() for idea in ideas]
        
        if ideas_dict:
            await ideas_collection.insert_many(ideas_dict)
            # Retirer les _id ajoutés par MongoDB
            for idea_dict in ideas_dict:
                idea_dict.pop('_id', None)
        
        return ideas_dict
    
    async def _generate_script_for_custom_idea(self, idea_id: str, script_text: str):
        """
        Générer un script pour une idée custom
        
        Args:
            idea_id: ID de l'idée
            script_text: Texte du script personnalisé
        """
        try:
            # Vérifier si un script existe déjà pour cette idée
            scripts_collection = get_scripts_collection()
            existing_script = await scripts_collection.find_one({"idea_id": idea_id}, {"_id": 0})
            
            if existing_script:
                print(f"⚠️  Script déjà existant pour l'idée {idea_id}, mise à jour en cours...")
                # Mettre à jour le script existant
                await scripts_collection.update_one(
                    {"idea_id": idea_id},
                    {"$set": {
                        "original_script": script_text,
                        "elevenlabs_adapted_script": None,
                        "phrases": []
                    }}
                )
            else:
                # Créer un nouveau script
                ideas_collection = get_ideas_collection()
                idea = await ideas_collection.find_one({"id": idea_id}, {"_id": 0})
                
                if not idea:
                    raise ValueError(f"Idea {idea_id} not found")
                
                script = Script(
                    idea_id=idea_id,
                    title=idea["title"],
                    original_script=script_text
                )
                
                await scripts_collection.insert_one(script.model_dump())
                
                # Mettre à jour l'idée avec l'ID du script
                await ideas_collection.update_one(
                    {"id": idea_id},
                    {"$set": {
                        "status": IdeaStatus.SCRIPT_GENERATED,
                        "script_id": script.id
                    }}
                )
            
            print(f"✅ Script généré pour l'idée custom {idea_id}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération du script pour l'idée custom {idea_id}: {str(e)}")
            raise
