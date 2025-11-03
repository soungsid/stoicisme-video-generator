import os
from typing import Tuple
from openai import AsyncOpenAI

class ScriptGeneratorAgent:
    """
    Agent IA pour générer des scripts de vidéos
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
    
    async def generate_script(self, title: str, keywords: list, duration_seconds: int) -> any:
        """
        Générer un script pour une vidéo
        """
        from models import Script
        
        # Estimer le nombre de mots (environ 150 mots par minute de parole)
        words_per_minute = 150
        target_words = int((duration_seconds / 60) * words_per_minute)
        
        prompt = f"""
Tu es un scénariste expert spécialisé dans le contenu YouTube sur le stoïcisme.

Crée un script captivant pour une vidéo YouTube avec les paramètres suivants:

TITRE: {title}
MOTS-CLÉS: {', '.join(keywords)}
DURÉE: {duration_seconds} secondes (environ {target_words} mots)

Le script doit:
1. Captiver dès les 3 premières secondes (hook fort)
2. Être conversationnel et engageant (comme si tu parlais à un ami)
3. Donner des conseils pratiques et actionnables
4. Utiliser des exemples concrets du stoïcisme (Marc Aurèle, Sénèque, Épictète)
5. Se terminer par un appel à l'action (like, subscribe, comment)
6. Être rythmé avec des phrases courtes et percutantes
7. Inclure des transitions naturelles
8. Être précis et respecter la durée cible

Structure recommandée:
- Hook (5-10 secondes): Accroche forte qui pose le problème
- Introduction (10-15% du temps): Contexte et promesse
- Développement (70-75% du temps): Contenu principal avec exemples
- Conclusion (10-15% du temps): Résumé et appel à l'action

Écris UNIQUEMENT le script, sans annotations ni instructions de mise en scène.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un scénariste expert en contenu YouTube sur le stoïcisme."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            script_text = response.choices[0].message.content.strip()
            
            script = Script(
                idea_id="",  # Sera défini par l'appelant
                title=title,
                original_script=script_text
            )
            
            print(f"✅ Generated script: {len(script_text)} characters")
            return script
            
        except Exception as e:
            print(f"❌ Error generating script: {str(e)}")
            raise
