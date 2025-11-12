from typing import Optional, List, Dict
from database import get_videos_collection

class RelatedVideoService:
    """
    Service pour trouver des vidéos liées basé sur les mots-clés et le thème
    Permet de créer des liens entre vidéos pour améliorer l'engagement
    """
    
    def __init__(self):
        self.videos_collection = get_videos_collection()
    
    async def find_related_video(
        self,
        current_video_id: str,
        keywords: List[str],
        theme: str = None
    ) -> Optional[Dict]:
        """
        Trouver une vidéo liée basée sur les mots-clés et le thème
        
        Args:
            current_video_id: ID de la vidéo actuelle (à exclure)
            keywords: Liste de mots-clés de la vidéo actuelle
            theme: Thème optionnel pour affiner la recherche
            
        Returns:
            Dictionnaire avec les infos de la vidéo liée ou None
        """
        
        try:
            # Récupérer toutes les vidéos uploadées sauf la vidéo actuelle
            videos = await self.videos_collection.find({
                "id": {"$ne": current_video_id},
                "youtube_video_id": {"$exists": True, "$ne": None}
            }, {"_id": 0}).to_list(length=None)
            
            if not videos:
                print("⚠️  Aucune vidéo uploadée disponible pour la recommandation")
                return None
            
            # Récupérer les idées associées pour avoir accès aux keywords
            from database import get_ideas_collection
            ideas_collection = get_ideas_collection()
            
            # Scorer chaque vidéo basé sur la similarité des mots-clés
            scored_videos = []
            
            for video in videos:
                idea_id = video.get("idea_id")
                if not idea_id:
                    continue
                
                idea = await ideas_collection.find_one(
                    {"id": idea_id},
                    {"_id": 0, "keywords": 1, "title": 1}
                )
                
                if not idea:
                    continue
                
                video_keywords = idea.get("keywords", [])
                video_title = idea.get("title", video.get("title", ""))
                
                # Calculer le score de similarité
                score = self._calculate_similarity_score(
                    keywords, 
                    video_keywords,
                    theme,
                    video_title
                )
                
                if score > 0:
                    scored_videos.append({
                        "video": video,
                        "idea": idea,
                        "score": score
                    })
            
            if not scored_videos:
                print("⚠️  Aucune vidéo similaire trouvée")
                return None
            
            # Trier par score décroissant et prendre la meilleure
            scored_videos.sort(key=lambda x: x["score"], reverse=True)
            best_match = scored_videos[0]
            
            print(f"✅ Vidéo liée trouvée: {best_match['idea']['title']} (score: {best_match['score']})")
            
            return {
                "id": best_match["video"]["id"],
                "title": best_match["idea"]["title"],
                "youtube_url": best_match["video"]["youtube_url"],
                "youtube_video_id": best_match["video"]["youtube_video_id"],
                "keywords": best_match["idea"]["keywords"],
                "similarity_score": best_match["score"]
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche de vidéo liée: {str(e)}")
            return None
    
    def _calculate_similarity_score(
        self,
        current_keywords: List[str],
        video_keywords: List[str],
        theme: str,
        video_title: str
    ) -> float:
        """
        Calculer le score de similarité entre la vidéo actuelle et une autre vidéo
        
        Args:
            current_keywords: Mots-clés de la vidéo actuelle
            video_keywords: Mots-clés de la vidéo candidate
            theme: Thème de la vidéo actuelle
            video_title: Titre de la vidéo candidate
            
        Returns:
            Score de similarité (plus élevé = plus similaire)
        """
        
        score = 0.0
        
        # Normaliser les mots-clés en minuscules
        current_kw_lower = [kw.lower() for kw in current_keywords]
        video_kw_lower = [kw.lower() for kw in video_keywords]
        
        # 1. Score basé sur les mots-clés communs (poids: 3 points par mot-clé)
        common_keywords = set(current_kw_lower) & set(video_kw_lower)
        score += len(common_keywords) * 3.0
        
        # 2. Score basé sur les mots-clés similaires (poids: 1 point)
        for current_kw in current_kw_lower:
            for video_kw in video_kw_lower:
                if current_kw != video_kw:
                    # Vérifier si un mot-clé contient l'autre
                    if current_kw in video_kw or video_kw in current_kw:
                        score += 1.0
        
        # 3. Score basé sur le thème dans le titre (poids: 5 points)
        if theme:
            theme_lower = theme.lower()
            title_lower = video_title.lower()
            
            # Vérifier si le thème apparaît dans le titre
            if theme_lower in title_lower:
                score += 5.0
            
            # Vérifier si des mots du thème apparaissent
            theme_words = theme_lower.split()
            for word in theme_words:
                if len(word) > 3 and word in title_lower:  # Ignorer les petits mots
                    score += 1.0
        
        # 4. Pénalité si aucun mot-clé en commun (rendre moins pertinent)
        if len(common_keywords) == 0:
            score *= 0.5
        
        return score
    
    async def get_video_recommendations(
        self,
        current_video_id: str,
        keywords: List[str],
        limit: int = 3
    ) -> List[Dict]:
        """
        Obtenir une liste de recommandations de vidéos
        
        Args:
            current_video_id: ID de la vidéo actuelle
            keywords: Mots-clés de la vidéo actuelle
            limit: Nombre maximum de recommandations
            
        Returns:
            Liste de vidéos recommandées
        """
        
        try:
            videos = await self.videos_collection.find({
                "id": {"$ne": current_video_id},
                "youtube_video_id": {"$exists": True, "$ne": None}
            }, {"_id": 0}).to_list(length=None)
            
            if not videos:
                return []
            
            from database import get_ideas_collection
            ideas_collection = get_ideas_collection()
            
            scored_videos = []
            
            for video in videos:
                idea_id = video.get("idea_id")
                if not idea_id:
                    continue
                
                idea = await ideas_collection.find_one(
                    {"id": idea_id},
                    {"_id": 0, "keywords": 1, "title": 1}
                )
                
                if not idea:
                    continue
                
                video_keywords = idea.get("keywords", [])
                video_title = idea.get("title", video.get("title", ""))
                
                score = self._calculate_similarity_score(
                    keywords,
                    video_keywords,
                    None,
                    video_title
                )
                
                if score > 0:
                    scored_videos.append({
                        "id": video["id"],
                        "title": idea["title"],
                        "youtube_url": video["youtube_url"],
                        "youtube_video_id": video["youtube_video_id"],
                        "keywords": idea["keywords"],
                        "score": score
                    })
            
            # Trier et limiter
            scored_videos.sort(key=lambda x: x["score"], reverse=True)
            return scored_videos[:limit]
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des recommandations: {str(e)}")
            return []
