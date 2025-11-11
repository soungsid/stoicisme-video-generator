"""
Service pour gérer la configuration LLM
"""

from typing import Dict
import os
import traceback


class LlmConfigService:
    """
    Service pour gérer la configuration LLM (DeepSeek, OpenAI, Gemini)
    """
    
    def __init__(self):
        pass
    
    async def get_config(self) -> Dict:
        """
        Récupérer la configuration LLM
        
        Returns:
            dict: Configuration LLM complète
        """
        try:
            provider = os.getenv("AI_PROVIDER", "deepseek")
            
            config = {
                "provider": provider,
                "deepseek": {
                    "configured": bool(os.getenv("DEEPSEEK_API_KEY")),
                    "model": os.getenv("DEEPSEEK_MODEL")
                },
                "openai": {
                    "configured": bool(os.getenv("OPENAI_API_KEY")) and os.getenv("OPENAI_API_KEY") != "your-openai-api-key-here",
                    "model": os.getenv("OPENAI_MODEL")
                },
                "gemini": {
                    "configured": bool(os.getenv("GEMINI_API_KEY")) and os.getenv("GEMINI_API_KEY") != "your-gemini-api-key-here",
                    "model": os.getenv("GEMINI_MODEL")
                }
            }
            
            return config
            
        except Exception as e:
            print(f"❌ Error fetching LLM config: {str(e)}")
            traceback.print_exc()
            raise
