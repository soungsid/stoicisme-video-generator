from typing import List
from agents.base_agent import BaseAIAgent

class SectionTitleGeneratorAgent(BaseAIAgent):
    """
    Agent IA pour générer les titres de sections pour vidéos longues
    """
    
    def __init__(self):
        super().__init__()
    
    async def generate_section_titles(
        self, 
        title: str, 
        keywords: List[str], 
        sections_count: int
    ) -> List[str]:
        """
        Générer les titres de sections pour une vidéo longue
        
        Args:
            title: Titre principal de la vidéo
            keywords: Mots-clés de la vidéo
            sections_count: Nombre de sections à générer
            
        Returns:
            Liste des titres de sections
        """
        
        prompt = f"""
Tu es un expert en structuration de contenu vidéo éducatif.

Génère {sections_count} titres de sections pour une vidéo YouTube avec les paramètres suivants:

TITRE PRINCIPAL: {title}
MOTS-CLÉS: {', '.join(keywords)}
NOMBRE DE SECTIONS: {sections_count}

Les titres de sections doivent:
1. Être clairs et descriptifs
2. Former une progression logique qui développe le titre principal
3. Être engageants et donner envie de regarder
4. Être concis (5-8 mots maximum)
5. Couvrir différents aspects du sujet
6. Être cohérents entre eux

IMPORTANT: 
- Ne génère PAS les titres pour l'introduction et la conclusion (ils seront ajoutés automatiquement)
- Les sections doivent constituer le corps principal de la vidéo
- Retourne UNIQUEMENT les titres, un par ligne, numérotés de 1 à {sections_count}
- Format: "1. Premier titre de section"

Exemple pour "Les 5 principes du stoïcisme" avec 3 sections:
1. Le contrôle de soi face aux émotions négatives
2. L'acceptation de ce qui ne dépend pas de nous
3. La pratique quotidienne de la gratitude

Génère maintenant les {sections_count} titres:
"""
        
        try:
            response = await self.generate_completion(
                system_prompt="Tu es un expert en structuration de contenu vidéo éducatif et philosophique.",
                user_prompt=prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parser la réponse pour extraire les titres
            lines = response.strip().split('\n')
            section_titles = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Retirer la numérotation si présente (ex: "1. ", "1)", "1 -")
                for prefix in [f"{i}. " for i in range(1, sections_count + 1)] + \
                             [f"{i}) " for i in range(1, sections_count + 1)] + \
                             [f"{i} - " for i in range(1, sections_count + 1)]:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                        break
                
                if line:
                    section_titles.append(line)
            
            # S'assurer qu'on a le bon nombre de sections
            section_titles = section_titles[:sections_count]
            
            if len(section_titles) < sections_count:
                print(f"⚠️  Seulement {len(section_titles)} titres générés au lieu de {sections_count}")
            
            print(f"✅ {len(section_titles)} titres de sections générés")
            for i, title in enumerate(section_titles, 1):
                print(f"   {i}. {title}")
            
            return section_titles
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération des titres de sections: {str(e)}")
            raise
