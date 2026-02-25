# """
# Gemini API Service - Stateless Integration
# """

import asyncio
import json
import re  
import google.generativeai as genai
from typing import Dict, Any

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_TOKENS,
    REQUEST_TIMEOUT_SECONDS,
)

class GeminiService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL

    async def analyze(self, system_prompt: str, user_message: str) -> str:
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._call_gemini,
                    system_prompt,
                    user_message
                ),
                timeout=REQUEST_TIMEOUT_SECONDS
            )
            return response
        
        except asyncio.TimeoutError:
            return self._timeout_fallback()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._error_fallback(str(e))

    def _call_gemini(self, system_prompt: str, user_message: str) -> str:
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                contents=[{"role": "user", "parts": [f"{system_prompt}\n\n{user_message}"]}],
                generation_config={"temperature": 0.1}
            )
            
            text = response.text.strip()
            # Nettoyage des balises Markdown
            text = re.sub(r'```json|```', '', text).strip()
            
            try:
                data = json.loads(text)
                
                # SÉCURITÉ : Si Gemini a créé un JSON imbriqué par erreur
                # (ce qui semble être votre cas actuel)
                if isinstance(data, dict) and len(data) == 1 and list(data.keys())[0] in ["qualification", "response"]:
                    # On essaie d'extraire les données si elles sont cachées dans une string
                    # ou on renvoie tel quel si c'est déjà plat.
                    pass

                return json.dumps(data)
            except:
                # Si le JSON est vraiment corrompu, on renvoie une structure propre
                return self._error_fallback("L'IA a produit un format incompatible.")

        except Exception as e:
            return self._error_fallback(str(e))
        
    def _timeout_fallback(self) -> str:
        return json.dumps({
            "qualification": "Délai d'attente dépassé",
            "applicable_articles": [],
            "risks": "L'analyse a pris trop de temps.",
            "advice": "Veuillez réessayer avec une question plus courte.",
            "disclaimer": "Erreur système."
        })

    def _error_fallback(self, error: str) -> str:
        return json.dumps({
            "qualification": "Erreur d'analyse",
            "applicable_articles": [],
            "risks": f"Une erreur est survenue : {error[:100]}",
            "advice": "Contactez le support si le problème persiste.",
            "disclaimer": "Erreur système."
        })
# import asyncio
# import json
# import google.generativeai as genai

# from config import (
#     GEMINI_API_KEY,
#     GEMINI_MODEL,
#     GEMINI_TEMPERATURE,
#     GEMINI_MAX_TOKENS,
#     REQUEST_TIMEOUT_SECONDS,
# )

# class GeminiService:
#     """Handles all Gemini API interactions"""
    
#     def __init__(self):
#         if not GEMINI_API_KEY:
#             raise ValueError("GEMINI_API_KEY environment variable not set")
#         genai.configure(api_key=GEMINI_API_KEY)
#         self.model = GEMINI_MODEL
    
#     async def analyze(self, system_prompt: str, user_message: str) -> str:
#         """
#         Send structured prompt to Gemini and get response
        
#         Args:
#             system_prompt: System context + legal constraints
#             user_message: User query + extracted content
        
#         Returns:
#             Structured response from Gemini (raw text)
#         """
        
#         try:
#             loop = asyncio.get_event_loop()
#             response = await asyncio.wait_for(
#                 loop.run_in_executor(
#                     None,
#                     self._call_gemini,
#                     system_prompt,
#                     user_message
#                 ),
#                 timeout=REQUEST_TIMEOUT_SECONDS
#             )
#             return response
        
#         except asyncio.TimeoutError:
#             return self._timeout_fallback()
#         except Exception as e:
#             #return self._error_fallback(str(e))
#             import traceback
#             traceback.print_exc()
#             raise e
    
#     def _call_gemini(self, system_prompt: str, user_message: str) -> str:
#         """
#         Synchronous Gemini API call
#         """
        
#         try:
#             #genai.configure(api_key=GEMINI_API_KEY)
#             model = genai.GenerativeModel(self.model)
#             response = model.generate_content(
#                 contents=[
#                     {"role": "user", "parts": [system_prompt + "\n\n" + user_message]}
#                 ],
#                 generation_config={
#                     "temperature": GEMINI_TEMPERATURE,
#                     "max_output_tokens": GEMINI_MAX_TOKENS,
#                     "top_p": 0.9,
#                 },
#                 # safety_settings=[
#                 #     {
#                 #         "category": "HARM_CATEGORY_HATE_SPEECH",
#                 #         "threshold": "BLOCK_ALL"
#                 #     },
#                 #     {
#                 #         "category": "HARM_CATEGORY_HARASSMENT",
#                 #         "threshold": "BLOCK_ALL"
#                 #     }
#                 # ]
#             )
#             return response.text
        
#         except Exception as e:
#             #raise
#             import traceback
#             traceback.print_exc()
#             raise e 
    
#     def _timeout_fallback(self) -> str:
#         """Fallback response on timeout"""
#         return json.dumps({
#             "qualification": "Analysis timeout",
#             "applicable_articles": [],
#             "risks": "Unable to complete analysis",
#             "advice": "Please try again"
#         })
    
#     def _error_fallback(self, error: str) -> str:
#         """Fallback response on error"""
#         return json.dumps({
#             "qualification": "Analysis error",
#             "applicable_articles": [],
#             "risks": "System error occurred",
#             "advice": "Please retry"
#         }) 