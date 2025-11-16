from typing import List
from models import VideoIdea, IdeaStatus, IdeaGenerationRequest
from agents.base_agent import BaseAIAgent

class IdeaGeneratorAgent(BaseAIAgent):
    """
    Agent IA pour générer des idées de vidéos sur le stoïcisme
    """
    
    def __init__(self):
        super().__init__()
    
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
            content = await self.generate_completion(
                system_prompt="Tu es un expert en création de contenu YouTube spécialisé dans le stoïcisme.",
                user_prompt=prompt,
                temperature=0.8,
                max_tokens=4000
            )
            
            ideas = self._parse_ideas(content)
            
            print(f"✅ Generated {len(ideas)} video ideas")
            return ideas
            
        except Exception as e:
            print(f"❌ Error generating ideas: {str(e)}")
            raise
    
    async def generate_ideas_with_keywords(self, count: int = 5, keywords: List[str] = None) -> List[VideoIdea]:
        """
        Générer des idées avec des mots-clés spécifiques
        """
        keywords_str = ", ".join(keywords) if keywords else ""
        
        prompt = f"""
Tu es un expert en création de contenu YouTube sur le stoïcisme et la philosophie.

Génère {count} titres accrocheurs pour des vidéos YouTube sur le stoïcisme qui:
1. DOIVENT inclure ou être liés à ces mots-clés: {keywords_str}
2. Sont engageants et incitent au clic
3. Promettent une valeur pratique
4. Utilisent des formules qui fonctionnent

Pour chaque idée, fournis:
- Le titre complet (doit être lié aux mots-clés: {keywords_str})
- 3-5 mots-clés SEO (incluant ceux demandés)

Format de réponse:
TITRE: [titre]
KEYWORDS: [mot1, mot2, mot3]
---
"""
        
        try:
            content = await self.generate_completion(
                system_prompt="Tu es un expert en création de contenu YouTube spécialisé dans le stoïcisme.",
                user_prompt=prompt,
                temperature=0.8,
                max_tokens=2000
            )
            
            ideas = self._parse_ideas(content)
            
            print(f"✅ Generated {len(ideas)} video ideas with keywords: {keywords_str}")
            return ideas
            
        except Exception as e:
            print(f"❌ Error generating ideas: {str(e)}")
            raise
    
    async def generate_title_from_script(self, script_text: str, keywords: List[str] = None) -> str:
        """
        Générer un titre accrocheur à partir d'un script existant
        """
        keywords_str = ", ".join(keywords) if keywords else ""
        keywords_instruction = f"\n- Inclure ces mots-clés si pertinent: {keywords_str}" if keywords else ""
        
        prompt = f"""
Tu es un expert en création de titres YouTube viraux.

Voici un script de vidéo :

{script_text[:500]}...

Génère UN SEUL titre YouTube accrocheur qui:
1. Résume le contenu du script
2. Est engageant et incite au clic
3. Utilise une formule qui fonctionne ("3 Actions que vous regretterez toute votre vie", "4 Habitudes qui volent votre énergie sans que vous le sachiez", "Ce secret...", "Quand...", "Comment...")
4. Est optimisé pour le SEO{keywords_instruction}

Réponds UNIQUEMENT avec le titre, rien d'autre.
"""
        
        try:
            title = await self.generate_completion(
                system_prompt="Tu es un expert en création de titres YouTube.",
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=100
            )
            
            # Nettoyer le titre (enlever guillemets, etc.)
            title = title.strip().strip('"\'')
            
            print(f"✅ Generated title: {title}")
            return title
            
        except Exception as e:
            print(f"❌ Error generating title: {str(e)}")
            raise
    
    async def generate_idea(self, request: IdeaGenerationRequest, previously_generated_titles: List[str] = None) -> VideoIdea:
        """
        Générer une seule idée en prenant en compte tous les paramètres de la requête
        
        Args:
            request: Requête de génération d'idées
            previously_generated_titles: Liste des titres déjà générés pour éviter les doublons
            
        Returns:
            VideoIdea: Idée générée
        """
        # Construire le prompt en fonction des paramètres fournis
        prompt_parts = []
        
        # Instructions de base
        prompt_parts.append("""
Tu es un expert en création de contenu YouTube sur le stoïcisme et la philosophie.

Génère UN SEUL titre accrocheur pour une vidéo YouTube sur le stoïcisme qui:
1. Est engageant et incite au clic
2. Promet une valeur pratique (conseils, sagesse applicable)
3. Utilise des formules qui fonctionnent ("Ce secret...", "Quand...", "X habitudes/choses...")
4. Est adapté au format vidéo demandé
""")
        
        # Prendre en compte le titre personnalisé si fourni
        if request.custom_title:
            prompt_parts.append(f"""
IMPORTANT: Tu DOIS utiliser ou t'inspirer fortement de ce titre: "{request.custom_title}"
Le titre final doit être une version améliorée et optimisée de ce titre.
""")
        
        # Prendre en compte le script si fourni
        if request.script_text:
            prompt_parts.append(f"""
Le titre doit résumer ou être fortement lié à ce script:
{request.script_text[:500]}...
""")
        
        # Prendre en compte les mots-clés si fournis
        if request.keywords:
            keywords_str = ", ".join(request.keywords)
            prompt_parts.append(f"""
Le titre DOIT inclure ou être lié à ces mots-clés: {keywords_str}
""")
        
        # Prendre en compte les instructions spécifiques (type vidéo, durée)
        video_type_info = "short (9:16)" if request.video_type.value == "short" else "longue (16:9)"
        prompt_parts.append(f"""
Le titre doit être adapté pour une vidéo {video_type_info} d'environ {request.duration_seconds} secondes.
""")
        
        # Éviter les doublons si des titres précédents sont fournis
        if previously_generated_titles:
            prompt_parts.append(f"""
IMPORTANT: Évite absolument ces titres qui ont déjà été générés:
{chr(10).join(f"- {title}" for title in previously_generated_titles)}

Le titre doit être complètement différent et original.
""")
        
        # Instructions de format
        prompt_parts.append("""
Fournis:
- Le titre complet
- 3-5 mots-clés SEO pertinents

Format de réponse:
TITRE: [titre]
KEYWORDS: [mot1, mot2, mot3]
""")
        
        prompt = "\n".join(prompt_parts)
        
        try:
            content = await self.generate_completion(
                system_prompt="Tu es un expert en création de contenu YouTube spécialisé dans le stoïcisme.",
                user_prompt=prompt,
                temperature=0.8,
                max_tokens=1000
            )
            
            # Parser la réponse
            idea = self._parse_single_idea(content)
            
            # Appliquer les paramètres de la requête
            idea.video_type = request.video_type
            idea.duration_seconds = request.duration_seconds
            if request.video_type.value == "normal" and request.sections_count:
                idea.sections_count = request.sections_count
            
            print(f"✅ Generated idea: {idea.title}")
            return idea
            
        except Exception as e:
            print(f"❌ Error generating idea: {str(e)}")
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
    
    def _parse_single_idea(self, content: str) -> VideoIdea:
        """Parser une seule idée depuis la réponse du LLM"""
        lines = content.split("\n")
        title = None
        keywords = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("TITRE:") or line.startswith("TITLE:"):
                title = line.split(":", 1)[1].strip()
            elif line.startswith("KEYWORDS:") or line.startswith("MOTS-CLÉS:"):
                keywords_str = line.split(":", 1)[1].strip()
                keywords = [k.strip() for k in keywords_str.split(",")]
        
        if not title:
            # Si pas de format spécifique, prendre la première ligne comme titre
            title = content.strip().split("\n")[0].strip()
            title = title.strip('"\'')
        
        return VideoIdea(
            title=title,
            keywords=keywords,
            status=IdeaStatus.PENDING
        )
