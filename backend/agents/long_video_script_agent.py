from typing import List, Dict, Tuple
from agents.base_agent import BaseAIAgent
from models import VideoSection

class LongVideoScriptAgent(BaseAIAgent):
    """
    Agent IA pour générer des scripts de vidéos longues avec sections
    Génération séquentielle pour assurer la cohérence
    """
    
    def __init__(self):
        super().__init__()
    
    async def generate_introduction(
        self, 
        title: str, 
        keywords: List[str],
        section_titles: List[str]
    ) -> str:
        """
        Générer une introduction captivante (3-5 phrases)
        
        Args:
            title: Titre de la vidéo
            keywords: Mots-clés
            section_titles: Titres des sections qui suivront
            
        Returns:
            Script de l'introduction
        """
        
        sections_preview = "\n".join([f"- {title}" for title in section_titles])
        
        prompt = f"""
Tu es un scénariste expert pour YouTube. Crée une introduction CAPTIVANTE et COURTE.

TITRE: {title}
MOTS-CLÉS: {', '.join(keywords)}

SECTIONS QUI SUIVRONT:
{sections_preview}

L'introduction doit:
1. Faire exactement 3 à 5 phrases (pas plus!)
2. Éveiller la curiosité avec une question engageante
3. Utiliser des formules comme:
   - "Vous êtes-vous déjà demandé..."
   - "Et si..."
   - "Imaginez un instant..."
   - "Avez-vous remarqué que..."
4. Ne PAS être superficielle - poser une vraie question qui intrigue
5. Créer un sentiment d'urgence ou d'importance
6. Annoncer brièvement ce qui sera couvert

IMPORTANT: 
- Sois CONCIS (3-5 phrases maximum)
- Pas de formules creuses
- Directement engageant dès la première phrase

Écris UNIQUEMENT le script de l'introduction:
"""
        
        try:
            intro = await self.generate_completion(
                system_prompt="Tu es un scénariste expert en introductions captivantes pour YouTube.",
                user_prompt=prompt,
                temperature=0.8,
                max_tokens=500
            )
            
            print(f"✅ Introduction générée: {len(intro)} caractères")
            return intro.strip()
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération de l'introduction: {str(e)}")
            raise
    
    async def generate_section_script(
        self,
        section_number: int,
        section_title: str,
        main_title: str,
        keywords: List[str],
        duration_seconds: float,
        previous_sections: List[Dict[str, str]] = None
    ) -> str:
        """
        Générer le script d'une section en tenant compte des sections précédentes
        
        Args:
            section_number: Numéro de la section
            section_title: Titre de cette section
            main_title: Titre principal de la vidéo
            keywords: Mots-clés
            duration_seconds: Durée cible de cette section
            previous_sections: Liste des sections précédentes avec leurs titres et scripts
            
        Returns:
            Script de la section
        """
        
        # Calculer le nombre de mots cible (environ 150 mots/minute)
        words_per_minute = 150
        target_words = int((duration_seconds / 60) * words_per_minute)
        
        # Préparer le contexte des sections précédentes
        context = ""
        if previous_sections:
            context = "\n\nSECTIONS PRÉCÉDENTES (pour assurer la cohérence):\n"
            for prev in previous_sections:
                context += f"\n### {prev['title']}\n{prev['script'][:300]}...\n"
        
        prompt = f"""
Tu es un scénariste expert spécialisé dans le contenu YouTube éducatif sur le stoïcisme et la philosophie.

CONTEXTE:
- Titre principal: {main_title}
- Section actuelle: Section {section_number} - {section_title}
- Mots-clés: {', '.join(keywords)}
- Durée cible: {duration_seconds} secondes (environ {target_words} mots)
{context}

Crée le script de cette section avec ces exigences:

1. COHÉRENCE: Le script doit s'intégrer naturellement après les sections précédentes
2. TRANSITION: Commence par une transition fluide si ce n'est pas la première section
3. CONTENU:
   - Développe spécifiquement le thème "{section_title}"
   - Donne des exemples concrets et pratiques
   - Utilise des références au stoïcisme si pertinent (Marc Aurèle, Sénèque, Épictète)
   - Reste conversationnel et engageant
4. DURÉE: Respecte la durée cible de {target_words} mots
5. STYLE:
   - Phrases courtes et percutantes
   - Langage simple et accessible
   - Exemples concrets du quotidien
   - Évite les répétitions avec les sections précédentes

IMPORTANT:
- Ne crée PAS de conclusion pour cette section (elle viendra plus tard)
- Concentre-toi uniquement sur le développement de "{section_title}"
- Assure une progression logique par rapport aux sections précédentes

Écris UNIQUEMENT le script de cette section:
"""
        
        try:
            script = await self.generate_completion(
                system_prompt="Tu es un scénariste expert en contenu éducatif YouTube.",
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=4000
            )
            
            print(f"✅ Section {section_number} générée: {len(script)} caractères")
            return script.strip()
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération de la section {section_number}: {str(e)}")
            raise
    
    async def generate_full_script_with_sections(
        self,
        title: str,
        keywords: List[str],
        section_titles: List[str],
        total_duration_seconds: float
    ) -> Tuple[str, List[VideoSection]]:
        """
        Générer le script complet avec toutes les sections de manière séquentielle
        
        Args:
            title: Titre de la vidéo
            keywords: Mots-clés
            section_titles: Titres des sections
            total_duration_seconds: Durée totale de la vidéo
            
        Returns:
            Tuple (script_complet, liste_des_sections)
        """
        
        print(f"\n🎬 Génération du script long pour: {title}")
        print(f"   Sections: {len(section_titles)}")
        print(f"   Durée totale: {total_duration_seconds}s")
        
        # Calculer la répartition du temps
        # Introduction et conclusion: ~3-5 phrases chacune (environ 15-20 secondes)
        intro_duration = 15  # secondes
        conclusion_duration = 20  # secondes
        
        # Durée restante pour les sections (équilibrée)
        remaining_duration = total_duration_seconds - intro_duration - conclusion_duration
        section_duration = remaining_duration / len(section_titles)
        
        print(f"   Durée par section: ~{section_duration:.1f}s")
        
        # 1. Générer l'introduction
        print("\n📝 Génération de l'introduction...")
        introduction = await self.generate_introduction(title, keywords, section_titles)
        
        # 2. Générer les sections séquentiellement
        sections = []
        previous_sections = []
        current_time = intro_duration
        
        for i, section_title in enumerate(section_titles, 1):
            print(f"\n📝 Génération de la section {i}/{len(section_titles)}: {section_title}")
            
            section_script = await self.generate_section_script(
                section_number=i,
                section_title=section_title,
                main_title=title,
                keywords=keywords,
                duration_seconds=section_duration,
                previous_sections=previous_sections if previous_sections else None
            )
            
            section = VideoSection(
                section_number=i,
                title=section_title,
                script=section_script,
                duration_seconds=section_duration,
                start_time=current_time,
                end_time=current_time + section_duration
            )
            
            sections.append(section)
            previous_sections.append({
                'title': section_title,
                'script': section_script
            })
            
            current_time += section_duration
        
        # 3. Assembler le script complet
        full_script_parts = [
            "=== INTRODUCTION ===",
            introduction,
            ""
        ]
        
        for section in sections:
            full_script_parts.extend([
                f"=== SECTION {section.section_number}: {section.title} ===",
                section.script,
                ""
            ])
        
        full_script = "\n".join(full_script_parts)
        
        print(f"\n✅ Script complet généré: {len(full_script)} caractères")
        print(f"   Introduction + {len(sections)} sections")
        
        return full_script, sections
