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
        Créer des idées de vidéos selon la nouvelle structure
        
        Args:
            request: Requête de génération d'idées
            
        Returns:
            dict: Résultat de la création avec les idées générées
        """
        try:
            ideas = []
            count = request.count
            
            # Si request.count n'est pas défini ou est égal à 0, count = 1
            if not count or count == 0:
                count = 1
            
            # Boucler de 1 à count
            previously_generated_titles = []
            for i in range(count):
                idea = await self.generer_une_idee(request, previously_generated_titles)
                ideas.append(idea)
                previously_generated_titles.append(idea.title)
                print(f"✅ Idée {i+1}/{count} générée: {idea.title}")
            
            # Générer les titres de sections si nécessaire
            if request.video_type.value == "normal" and request.sections_count and request.sections_count > 0:
                await self._generate_section_titles(ideas, request.sections_count)
            
            # Sauvegarder en base de données
            print(f"💾 Sauvegarde de {len(ideas)} idées...")
            ideas_dict = await self._save_ideas(ideas)
            print(f"✅ {len(ideas_dict)} idées sauvegardées")
            
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
    
    async def generer_une_idee(self, request: IdeaGenerationRequest, previously_generated_titles: List[str]) -> VideoIdea:
        """
        Générer une seule idée en prenant en compte tous les paramètres
        
        Args:
            request: Requête de génération d'idées
            previously_generated_titles: Liste des titres déjà générés
            
        Returns:
            VideoIdea: Idée générée
        """
        # Générer le titre si la request ne contient pas de titre
        if request.custom_title:
            title = request.custom_title
            print(f"✨ Utilisation du titre personnalisé: {title}")
        else:
            # Utiliser la méthode unifiée de génération
            idea = await self.idea_generator.generate_idea(request, previously_generated_titles)
            title = idea.title
        
        # Construire l'objet VideoIdea
        video_idea = VideoIdea(
            title=title,
            keywords=request.keywords or [],
            video_type=request.video_type,
            duration_seconds=request.duration_seconds,
            sections_count=request.sections_count if request.video_type.value == "normal" else None,
            status=IdeaStatus.PENDING
        )
        
        # Persister en base de données
        await self._save_single_idea(video_idea)
        
        # Si request.sections_count est supérieur à zéro, générer les titres des sections
        if request.video_type.value == "normal" and request.sections_count and request.sections_count > 0:
            await self._generate_section_titles_for_single_idea(video_idea, request.sections_count)
        
        # Si request.script_text existe, appeler le service de génération de script
        if request.script_text:
            await self._generate_script_for_idea(video_idea.id, request.script_text)
        
        return video_idea
    
    async def _save_single_idea(self, idea: VideoIdea):
        """Sauvegarder une seule idée en base de données"""
        try:
            ideas_collection = get_ideas_collection()
            await ideas_collection.insert_one(idea.model_dump())
            print(f"💾 Idée sauvegardée: {idea.title}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde idée {idea.title}: {e}")
            raise
    
    async def _generate_section_titles_for_single_idea(self, idea: VideoIdea, sections_count: int):
        """Générer les titres de sections pour une seule idée"""
        try:
            section_agent = SectionTitleGeneratorAgent()
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
    
    async def _generate_script_for_idea(self, idea_id: str, script_text: str):
        """
        Générer un script pour une idée
        
        Args:
            idea_id: ID de l'idée
            script_text: Texte du script personnalisé
        """
        try:
            # Mettre à jour l'idée avec le script original
            ideas_collection = get_ideas_collection()
            await ideas_collection.update_one(
                {"id": idea_id},
                {"$set": {
                    "original_script": script_text,
                    "status": IdeaStatus.SCRIPT_GENERATED
                }}
            )
            print(f"✅ Script associé à l'idée {idea_id}")
        except Exception as e:
            print(f"❌ Erreur association script pour l'idée {idea_id}: {str(e)}")
            raise
    
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
        try:
            ideas_dict = [idea.model_dump() for idea in ideas]
            
            if ideas_dict:
                ideas_collection = get_ideas_collection()
                await ideas_collection.insert_many(ideas_dict)
                # Retirer les _id ajoutés par MongoDB
                for idea_dict in ideas_dict:
                    idea_dict.pop('_id', None)
            
            return ideas_dict
        except Exception as e:
            print(f"❌ Erreur dans _save_ideas: {e}")
            raise
