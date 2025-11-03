import os
from typing import List
from models import VideoIdea, VideoType, IdeaStatus
from openai import AsyncOpenAI

class IdeaGeneratorAgent:
    """
    Agent IA pour générer des idées de vidéos sur le stoïcisme
    """
    
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "deepseek")
        
        if self.provider == "deepseek":
            self.client = AsyncOpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL")
            )
            self.model = os.getenv("DEEPSEEK_MODEL")
        elif self.provider == "openai":
            self.client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = os.getenv("OPENAI_MODEL")
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    async def generate_ideas(self, count: int = 5) -> List[VideoIdea]:
        """
        Générer des idées de vidéos
        """
        prompt = f"""
Tu es un expert en création de contenu YouTube sur le stoïcisme et la philosophie.

Génère {count} titres accrocheurs pour des vidéos YouTube sur le stoïcisme qui:
1. Sont engageants et incitent au clic
2. Promettent une valeur pratique (conseils, sagesse applicable)
3. Utilisent des formules qui fonctionnent ("Ce secret...", "Quand...", "X habitudes/choses...")
4. Sont adaptés aux shorts ET aux vidéos longues
5. Incluent des mots-clés SEO pertinents

Exemples de bons titres:
- "Quand quelqu'un ne vous apprécie pas, faites CECI | Sagesse stoïque"
- "Ce secret stoïque les rendra obsédés par vous | Stoïcisme"
- "5 Habitudes terribles que vous ne devez absolument pas prendre!"
- "Comment le stoïcisme peut transformer votre vie en 30 jours"
- "Marc Aurèle révèle: Le secret d'une vie sans stress"

Pour chaque idée, fournis:
- Le titre complet
- 3-5 mots-clés SEO pertinents

Format de réponse (une idée par ligne):
TITRE: [titre]
KEYWORDS: [mot1, mot2, mot3]
---
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un expert en création de contenu YouTube spécialisé dans le stoïcisme."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            ideas = self._parse_ideas(content)
            
            print(f"✅ Generated {len(ideas)} video ideas")
            return ideas
            
        except Exception as e:
            print(f"❌ Error generating ideas: {str(e)}")
            raise
    
    def _parse_ideas(self, content: str) -> List[VideoIdea]:
        """Parser les idées depuis la réponse du LLM"""
        ideas = []
        sections = content.split("---")
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            lines = section.split("\n")
            title = None
            keywords = []
            
            for line in lines:
                line = line.strip()
                if line.startswith("TITRE:") or line.startswith("TITLE:"):
                    title = line.split(":", 1)[1].strip()
                elif line.startswith("KEYWORDS:") or line.startswith("MOTS-CLÉS:"):
                    keywords_str = line.split(":", 1)[1].strip()
                    keywords = [k.strip() for k in keywords_str.split(",")]
            
            if title:
                idea = VideoIdea(
                    title=title,
                    keywords=keywords,
                    status=IdeaStatus.PENDING
                )
                ideas.append(idea)
        
        return ideas
