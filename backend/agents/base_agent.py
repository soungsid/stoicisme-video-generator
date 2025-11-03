import os
from openai import AsyncOpenAI
from typing import Optional

class BaseAIAgent:
    """
    Classe de base pour tous les agents IA
    Gère la configuration du provider LLM (DeepSeek, OpenAI, Gemini)
    """
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialise l'agent avec le provider LLM configuré
        
        Args:
            provider: 'deepseek', 'openai', ou 'gemini'. Si None, utilise AI_PROVIDER de .env
        """
        self.provider = provider or os.getenv("AI_PROVIDER", "deepseek")
        self.client = None
        self.model = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client LLM selon le provider configuré"""
        if self.provider == "deepseek":
            self.client = AsyncOpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL")
            )
            self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            
        elif self.provider == "openai":
            self.client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
            
        elif self.provider == "gemini":
            # Pour Gemini, on utilise l'API compatible OpenAI
            self.client = AsyncOpenAI(
                api_key=os.getenv("GEMINI_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            
        else:
            raise ValueError(f"Provider LLM non supporté: {self.provider}")
        
        print(f"✅ Agent IA initialisé avec {self.provider.upper()} - Modèle: {self.model}")
    
    async def generate_completion(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Génère une completion avec le LLM configuré
        
        Args:
            system_prompt: Instructions système pour le LLM
            user_prompt: Prompt utilisateur
            temperature: Créativité (0-1)
            max_tokens: Nombre maximum de tokens
            
        Returns:
            Réponse du LLM
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération: {str(e)}")
            raise
