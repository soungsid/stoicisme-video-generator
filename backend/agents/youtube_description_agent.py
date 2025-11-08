from typing import List
from agents.base_agent import BaseAIAgent

class YouTubeDescriptionAgent(BaseAIAgent):
    """
    Agent IA pour générer des descriptions YouTube optimisées SEO
    """
    
    def __init__(self):
        super().__init__()
    
    async def generate_description(
        self, 
        title: str, 
        script: str, 
        keywords: List[str] = None
    ) -> str:
        """
        Générer une description YouTube optimisée
        """
        keywords_str = ", ".join(keywords) if keywords else "stoïcisme, philosophie"
        
        prompt = f"""
Tu es un expert en optimisation YouTube et SEO.

Génère une description YouTube optimisée pour cette vidéo:

TITRE: {title}

SCRIPT (extrait):
{script[:500]}...

MOTS-CLÉS: {keywords_str}

La description doit:
1. Commencer par un hook captivant (2-3 phrases)
2. Résumer le contenu de la vidéo
3. Inclure naturellement les mots-clés pour le SEO
4. Ajouter un CTA (appel à l'action) pour like/subscribe/comment
5. Inclure 5-10 hashtags pertinents à la fin
6. Être entre 150-300 mots
7. Être engageante et optimisée pour l'algorithme YouTube

Structure recommandée:
- Hook (pourquoi regarder cette vidéo)
- Résumé du contenu
- Ce que le spectateur va apprendre/gagner
- CTA (like, subscribe, notification bell)
- Liens utiles (si applicable)
- Hashtags

Réponds UNIQUEMENT avec la description, sans titre ni annotations.
"""
        
        try:
            description = await self.generate_completion(
                system_prompt="Tu es un expert en optimisation YouTube et marketing de contenu.",
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            print(f"✅ Description YouTube générée: {len(description)} caractères")
            return description
            
        except Exception as e:
            print(f"❌ Error generating YouTube description: {str(e)}")
            raise
