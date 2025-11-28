from agents.base_agent import BaseAIAgent
import re
from typing import List

class ImagePromptGeneratorAgent(BaseAIAgent):
    """
    Agent IA pour subdiviser un script en phrases sémantiques et générer des prompts d'images
    """
    
    def __init__(self):
        super().__init__()
    
    async def generate_image_prompts(self, script_text: str) -> List[str]:
        """
        Subdivise un script en phrases sémantiques et génère des prompts d'images
        
        Args:
            script_text: Le texte complet du script
            
        Returns:
            Liste des prompts d'images pour chaque subdivision
        """
        try:
            # D'abord, subdiviser le script en phrases sémantiques
            semantic_sections = await self._subdivide_script(script_text)
            
            # Ensuite, générer un prompt d'image pour chaque section
            image_prompts = []
            for i, section in enumerate(semantic_sections):
                prompt = await self._generate_single_prompt(section, i + 1, len(semantic_sections))
                image_prompts.append(prompt)
            
            print(f"✅ Generated {len(image_prompts)} image prompts from {len(semantic_sections)} semantic sections")
            return image_prompts
            
        except Exception as e:
            print(f"❌ Error generating image prompts: {str(e)}")
            raise
    
    async def _subdivide_script(self, script_text: str) -> List[str]:
        """
        Subdivise le script en sections sémantiques de 2-3 phrases
        """
        # Nettoyer le script
        clean_script = self._clean_script(script_text)
        
        # Diviser en phrases
        sentences = self._split_into_sentences(clean_script)
        
        # Grouper en sections de 2-3 phrases
        sections = self._group_sentences(sentences)
        
        # Si le script est très long, limiter à environ 20 sections
        if len(sections) > 20:
            sections = self._consolidate_sections(sections, target_count=20)
        
        return sections
    
    def _clean_script(self, script_text: str) -> str:
        """Nettoie le script en supprimant les éléments non pertinents"""
        # Supprimer les numéros de ligne, timestamps, etc.
        clean_text = re.sub(r'^\d+\.?\s*', '', script_text, flags=re.MULTILINE)
        clean_text = re.sub(r'\[\d+:\d+\]', '', clean_text)
        clean_text = re.sub(r'\([^)]*\)', '', clean_text)
        
        # Supprimer les espaces multiples
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return clean_text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divise le texte en phrases"""
        # Séparation basique par ponctuation
        sentences = re.split(r'[.!?]+', text)
        
        # Filtrer les phrases vides et nettoyer
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _group_sentences(self, sentences: List[str]) -> List[str]:
        """Groupe les phrases en sections de 2-3 phrases"""
        sections = []
        current_group = []
        
        for sentence in sentences:
            current_group.append(sentence)
            
            # Grouper par 2-3 phrases, ou si la phrase est très longue
            if len(current_group) >= 3 or len(sentence) > 100:
                sections.append(' '.join(current_group))
                current_group = []
        
        # Ajouter le dernier groupe s'il n'est pas vide
        if current_group:
            sections.append(' '.join(current_group))
        
        return sections
    
    def _consolidate_sections(self, sections: List[str], target_count: int) -> List[str]:
        """Consolide les sections pour atteindre un nombre cible"""
        if len(sections) <= target_count:
            return sections
        
        # Calculer combien de sections fusionner
        merge_factor = len(sections) // target_count + 1
        
        consolidated = []
        for i in range(0, len(sections), merge_factor):
            group = sections[i:i + merge_factor]
            consolidated.append(' '.join(group))
        
        return consolidated
    
    async def _generate_single_prompt(self, section_text: str, section_num: int, total_sections: int) -> str:
        """
        Génère un prompt d'image pour une section spécifique
        """
        prompt = f"""
Tu es un expert en génération d'images IA. Crée un prompt détaillé pour générer une image qui illustre parfaitement le contenu suivant:

SECTION {section_num}/{total_sections}:
"{section_text}"

Le prompt doit:
1. Être en anglais (pour une meilleure compatibilité avec les modèles d'IA)
2. Décrire une scène visuelle concrète et évocatrice
3. Inclure des détails sur l'ambiance, les couleurs, la composition
4. Être adapté au contenu stoïcien (si pertinent)
5. Être réaliste et cinématographique
6. Utiliser un style photographique ou artistique approprié
7. modern 2D animation style, clean line art, soft shading, warm colors, expressive faces


Exemple de format:
"cinematic shot of [description], [lighting], [composition], [style], [mood]"

Génère UNIQUEMENT le prompt, sans commentaires supplémentaires.
"""
        
        image_prompt = await self.generate_completion(
            system_prompt="Tu es un expert en génération d'images IA. Tu crées des prompts détaillés et évocateurs pour des images réalistes et cinématographiques.",
            user_prompt=prompt,
            temperature=0.8,
            max_tokens=300
        )
        
        return image_prompt.strip()
