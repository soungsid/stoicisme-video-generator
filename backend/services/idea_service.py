"""
Service pour gérer toute la logique métier des idées de vidéos
"""

from typing import List, Dict
from models import VideoIdea, IdeaStatus
from database import get_ideas_collection
from helpers.datetime_utils import now_utc
import traceback


class IdeaService:
    """
    Service pour gérer les idées de vidéos
    """
    
    def __init__(self):
        pass
    
    async def validate_idea(
        self, 
        idea_id: str, 
        video_type: str, 
        duration_seconds: int,
        keywords: List[str] = None
    ) -> Dict:
        """
        Valider une idée et définir ses paramètres
        
        Args:
            idea_id: ID de l'idée
            video_type: Type de vidéo (short, normal)
            duration_seconds: Durée en secondes
            keywords: Mots-clés optionnels
            
        Returns:
            dict: Idée validée
        """
        try:
            ideas_collection = get_ideas_collection()
            
            update_data = {
                "status": IdeaStatus.VALIDATED,
                "validated_at": now_utc(),
                "video_type": video_type,
                "duration_seconds": duration_seconds
            }
            
            if keywords:
                update_data["keywords"] = keywords
            
            result = await ideas_collection.find_one_and_update(
                {"id": idea_id},
                {"$set": update_data},
                return_document=True,
                projection={"_id": 0}
            )
            
            if not result:
                raise ValueError(f"Idea {idea_id} not found")
            
            print(f"✅ Idea {idea_id} validated")
            return result
            
        except Exception as e:
            print(f"❌ Error validating idea: {str(e)}")
            traceback.print_exc()
            raise
    
    async def reject_idea(self, idea_id: str) -> Dict:
        """
        Rejeter une idée
        
        Args:
            idea_id: ID de l'idée
            
        Returns:
            dict: Idée rejetée
        """
        try:
            ideas_collection = get_ideas_collection()
            
            result = await ideas_collection.find_one_and_update(
                {"id": idea_id},
                {"$set": {"status": IdeaStatus.REJECTED}},
                return_document=True,
                projection={"_id": 0}
            )
            
            if not result:
                raise ValueError(f"Idea {idea_id} not found")
            
            print(f"✅ Idea {idea_id} rejected")
            return result
            
        except Exception as e:
            print(f"❌ Error rejecting idea: {str(e)}")
            traceback.print_exc()
            raise
    
    async def delete_idea(self, idea_id: str) -> Dict:
        """
        Supprimer une idée
        
        Args:
            idea_id: ID de l'idée
            
        Returns:
            dict: Confirmation de suppression
        """
        try:
            ideas_collection = get_ideas_collection()
            result = await ideas_collection.delete_one({"id": idea_id})
            
            if result.deleted_count == 0:
                raise ValueError(f"Idea {idea_id} not found")
            
            print(f"✅ Idea {idea_id} deleted")
            return {
                "success": True,
                "message": "Idea deleted successfully"
            }
            
        except Exception as e:
            print(f"❌ Error deleting idea: {str(e)}")
            traceback.print_exc()
            raise
    
    async def batch_validate(self, idea_ids: List[str]) -> Dict:
        """
        Valider plusieurs idées en masse
        
        Args:
            idea_ids: Liste des IDs d'idées
            
        Returns:
            dict: Résultats de la validation en masse
        """
        try:
            ideas_collection = get_ideas_collection()
            
            results = {
                "success": [],
                "failed": []
            }
            
            for idea_id in idea_ids:
                try:
                    await ideas_collection.update_one(
                        {"id": idea_id},
                        {
                            "$set": {
                                "status": IdeaStatus.VALIDATED,
                                "validated_at": now_utc()
                            }
                        }
                    )
                    results["success"].append(idea_id)
                except Exception as e:
                    results["failed"].append({
                        "id": idea_id,
                        "reason": str(e)
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Error in batch validate: {str(e)}")
            traceback.print_exc()
            raise
    
    async def batch_reject(self, idea_ids: List[str]) -> Dict:
        """
        Rejeter plusieurs idées en masse
        
        Args:
            idea_ids: Liste des IDs d'idées
            
        Returns:
            dict: Résultats du rejet en masse
        """
        try:
            ideas_collection = get_ideas_collection()
            
            results = {
                "success": [],
                "failed": []
            }
            
            for idea_id in idea_ids:
                try:
                    await ideas_collection.update_one(
                        {"id": idea_id},
                        {"$set": {"status": IdeaStatus.REJECTED}}
                    )
                    results["success"].append(idea_id)
                except Exception as e:
                    results["failed"].append({
                        "id": idea_id,
                        "reason": str(e)
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Error in batch reject: {str(e)}")
            traceback.print_exc()
            raise
    
    async def batch_delete(self, idea_ids: List[str]) -> Dict:
        """
        Supprimer plusieurs idées en masse
        
        Args:
            idea_ids: Liste des IDs d'idées
            
        Returns:
            dict: Résultats de la suppression en masse
        """
        try:
            ideas_collection = get_ideas_collection()
            
            results = {
                "success": [],
                "failed": []
            }
            
            for idea_id in idea_ids:
                try:
                    await ideas_collection.delete_one({"id": idea_id})
                    results["success"].append(idea_id)
                except Exception as e:
                    results["failed"].append({
                        "id": idea_id,
                        "reason": str(e)
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Error in batch delete: {str(e)}")
            traceback.print_exc()
            raise
