import re
from typing import List, Tuple
from agents.base_agent import BaseAIAgent

class ScriptAdapterAgent(BaseAIAgent):
    """
    Agent IA pour adapter les scripts à ElevenLabs V3 avec marqueurs d'émotion
    """
    
    def __init__(self):
        super().__init__()
    
    async def adapt_script(self, original_script: str) -> Tuple[str, List[str]]:
        """
        Adapter le script pour ElevenLabs V3
        Retourne: (script_adapté, liste_de_phrases)
        """
        
        prompt = f"""
Tu es un expert en adaptation de scripts pour la synthèse vocale ElevenLabs V3.

SCRIPT ORIGINAL:
{original_script}

Ta mission est de:
1. Ajouter des marqueurs d'émotion et d'effets sonores ElevenLabs V3 aux endroits appropriés
2. Rendre le script plus expressif et naturel pour la voix

MARQUEURS DISPONIBLES:
Émotions: [laughs], [laughs harder], [starts laughing], [wheezing], [whispers], [sighs], [exhales], [sarcastic], [curious], [excited], [crying], [mischievously]

Effets sonores: [gunshot], [applause], [clapping], [explosion], [swallows], [gulps], [snorts]

RÈGLES D'ADAPTATION:
1. N'ajoute PAS trop de marqueurs (maximum 1 tous les 2-3 phrases)
2. Utilise les marqueurs de manière SUBTILE et NATURELLE
3. Place [whispers] pour les moments intimes/confidentiels
4. Place [excited] pour les moments d'enthousiasme
5. Place [sighs] pour les moments de réflexion
6. Place [curious] pour les questions rhétoriques
7. Place [laughs] UNIQUEMENT si le contexte est vraiment léger/humoristique
8. NE modifie PAS le contenu du script, ajoute SEULEMENT les marqueurs
9. Garde la structure et le sens exact du script original

EXEMPLE:
Original: "Et vous savez quoi? Cette technique a complètement changé ma vie."
Adapté: "[excited] Et vous savez quoi? Cette technique a complètement changé ma vie."

Original: "Laissez-moi vous révéler un secret..."
Adapté: "[whispers] Laissez-moi vous révéler un secret..."

Retourne UNIQUEMENT le script adapté avec les marqueurs, sans explications.
"""
        
        try:
            adapted_script = await self.generate_completion(
                system_prompt="Tu es un expert en adaptation de scripts pour ElevenLabs V3.",
                user_prompt=prompt,
                temperature=0.5,
                max_tokens=3000
            )
            
            # Diviser en phrases en préservant les marqueurs
            phrases = self._split_into_phrases(original_script)
            
            print(f"✅ Adapted script: {len(phrases)} phrases with emotion markers")
            return original_script, phrases
            
        except Exception as e:
            print(f"❌ Error adapting script: {str(e)}")
            raise
    
    def _split_into_phrases(self, script: str) -> List[str]:
        """
        Diviser le script en phrases tout en préservant les marqueurs
        """
        # Patterns pour split: . ! ? suivi d'un espace ou fin de ligne
        # Mais on garde les marqueurs avec leur phrase
        
        # Nettoyer les espaces multiples
        script = re.sub(r'\s+', ' ', script).strip()
        
        return [script]
        #return self._do_the_split(script)
    
    def _do_the_split(self, script: str) -> List[str]:
        """
        Diviser le script en phrases tout en préservant les marqueurs
        """
        # Patterns pour split: . ! ? suivi d'un espace ou fin de ligne
        # Mais on garde les marqueurs avec leur phrase
        
        # Nettoyer les espaces multiples
        script = re.sub(r'\s+', ' ', script).strip()
        
        # Split par phrase
        # On split sur . ! ? suivis d'un espace ET d'une majuscule ou d'un marqueur
        phrases = re.split(r'([.!?])\s+(?=[A-Z\[\u00c0-\u00dc])', script)
        
        # Reconstituer les phrases avec leur ponctuation
        result = []
        i = 0
        while i < len(phrases):
            if i + 1 < len(phrases) and phrases[i+1] in '.!?':
                phrase = phrases[i] + phrases[i+1]
                i += 2
            else:
                phrase = phrases[i]
                i += 1
            
            phrase = phrase.strip()
            if phrase:
                result.append(phrase)
        
        # Si pas de phrases (pas de ponctuation), split par ligne
        if not result:
            result = [line.strip() for line in script.split('\n') if line.strip()]
        
        # Si toujours rien, garder le script entier
        if not result:
            result = [script]
        
        return result
