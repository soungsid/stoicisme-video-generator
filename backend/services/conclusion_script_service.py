from typing import Optional, List
from agents.base_agent import BaseAIAgent
from services.related_video_service import RelatedVideoService

class ConclusionScriptService(BaseAIAgent):
    """
    Service dédié à la génération de conclusions pour vidéos longues
    Trouve une vidéo liée et crée un script pour inciter l'utilisateur à la regarder
    """
    
    def __init__(self):
        super().__init__()
        self.related_video_service = RelatedVideoService()
    
    async def generate_conclusion_with_recommendation(
        self,
        current_video_id: str,
        title: str,
        keywords: List[str],
        section_summaries: Optional[List[str]] = None
    ) -> str:
        """
        Générer une conclusion (3-5 phrases) avec recommandation de vidéo suivante
        
        Args:
            current_video_id: ID de la vidéo actuelle
            title: Titre de la vidéo actuelle
            keywords: Mots-clés de la vidéo actuelle
            section_summaries: Résumés des sections (optionnel)
            
        Returns:
            Script de la conclusion
        """
        
        print(f"\n📝 Génération de la conclusion avec recommandation...")
        
        # 1. Trouver une vidéo liée
        related_video = await self.related_video_service.find_related_video(
            current_video_id=current_video_id,
            keywords=keywords,
            theme=title
        )
        
        # 2. Générer la conclusion
        if related_video:
            conclusion = await self._generate_conclusion_with_related_video(
                title=title,
                keywords=keywords,
                related_video_title=related_video["title"],
                related_video_keywords=related_video["keywords"]
            )
        else:
            # Pas de vidéo liée trouvée, générer une conclusion simple
            conclusion = await self._generate_simple_conclusion(
                title=title,
                keywords=keywords
            )
        
        print(f"✅ Conclusion générée: {len(conclusion)} caractères")
        return conclusion
    
    async def _generate_conclusion_with_related_video(
        self,
        title: str,
        keywords: List[str],
        related_video_title: str,
        related_video_keywords: List[str]
    ) -> str:
        """
        Générer une conclusion qui recommande une vidéo spécifique
        """
        
        prompt = f"""
Tu es un scénariste expert pour YouTube. Crée une conclusion COURTE et ENGAGEANTE.

VIDÉO ACTUELLE:
- Titre: {title}
- Mots-clés: {', '.join(keywords)}

VIDÉO À RECOMMANDER:
- Titre: {related_video_title}
- Thème: {', '.join(related_video_keywords)}

La conclusion doit:
1. Faire exactement 3 à 5 phrases (pas plus!)
2. Résumer brièvement la valeur apportée par cette vidéo
3. Créer un lien naturel vers la vidéo recommandée
4. Utiliser des formules engageantes comme:
   - "Si vous avez apprécié le contenu de cette vidéo, vous aimerez aussi..."
   - "Pour aller plus loin sur ce sujet, je vous recommande..."
   - "Cette vidéo vous a plu ? Découvrez également..."
   - "Dans la même lignée, ne manquez pas..."
5. Mentionner explicitement que la vidéo suivante "s'affiche quelque part sur votre écran"
6. Rester sobre et succincte

IMPORTANT:
- Sois CONCIS (3-5 phrases maximum)
- Transition naturelle vers la recommandation
- Ton amical et encourageant

Exemple de structure:
[Phrase de résumé rapide]. [Lien vers le prochain sujet]. Si vous avez apprécié cette vidéo sur [thème actuel], vous adorerez celle qui parle de [thème suivant] qui s'affiche quelque part sur votre écran. [Call-to-action simple].

Écris UNIQUEMENT le script de la conclusion:
"""
        
        try:
            conclusion = await self.generate_completion(
                system_prompt="Tu es un scénariste expert en conclusions engageantes pour YouTube.",
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            return conclusion.strip()
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération de la conclusion: {str(e)}")
            raise
    
    async def _generate_simple_conclusion(
        self,
        title: str,
        keywords: List[str]
    ) -> str:
        """
        Générer une conclusion simple sans recommandation de vidéo
        """
        
        prompt = f"""
Tu es un scénariste expert pour YouTube. Crée une conclusion COURTE et SOBRE.

VIDÉO:
- Titre: {title}
- Mots-clés: {', '.join(keywords)}

La conclusion doit:
1. Faire exactement 3 à 5 phrases (pas plus!)
2. Résumer brièvement la valeur apportée
3. Remercier le spectateur
4. Encourager l'action (like, commentaire, abonnement) de manière subtile
5. Rester sobre et succincte

IMPORTANT:
- Sois CONCIS (3-5 phrases maximum)
- Pas de formules creuses
- Ton authentique et sincère

Écris UNIQUEMENT le script de la conclusion:
"""
        
        try:
            conclusion = await self.generate_completion(
                system_prompt="Tu es un scénariste expert en conclusions pour YouTube.",
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=400
            )
            
            return conclusion.strip()
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération de la conclusion simple: {str(e)}")
            raise
    
    async def add_conclusion_to_script(
        self,
        full_script: str,
        current_video_id: str,
        title: str,
        keywords: List[str]
    ) -> str:
        """
        Ajouter une conclusion à un script existant
        
        Args:
            full_script: Script actuel (introduction + sections)
            current_video_id: ID de la vidéo
            title: Titre de la vidéo
            keywords: Mots-clés
            
        Returns:
            Script complet avec conclusion
        """
        
        conclusion = await self.generate_conclusion_with_recommendation(
            current_video_id=current_video_id,
            title=title,
            keywords=keywords
        )
        
        # Ajouter la conclusion au script
        complete_script = full_script + "\n\n=== CONCLUSION ===\n" + conclusion
        
        return complete_script
