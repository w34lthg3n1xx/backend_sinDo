"""
Prompt Builder - Construct system and user prompts
Properly uses response structure from models
"""

from api.models import AnalysisResponse
from config import LEGAL_DISCLAIMER
import json

class PromptBuilder:
    """Build structured prompts for Gemini"""
    
    def build_system_prompt(self, legal_context: str) -> str:
        """
        Build system prompt with legal constraints and response format
        
        Args:
            legal_context: Relevant legal texts from database/
        
        Returns:
            System prompt with instructions and context
        """
        expected_structure = {
            "qualification": "string - legal classification",
            "applicable_articles": ["string", "string"],
            "risks": "string - legal consequences",
            "advice": "string - recommendations",
            "disclaimer": "string - legal disclaimer"
        }
        
        system_prompt = f"""You are a legal information assistant for a national digital legal aid application.

CONSTRAINTS:
1. Analyze only based on national legal frameworks provided below.
2. Provide GENERAL LEGAL INFORMATION, NOT PERSONALIZED LEGAL ADVICE.
3. MUST cite specific articles and laws when applicable.
4. MUST include the legal disclaimer in every response.
5. You refuse to:
    - Provide advice on how to break laws
    - Help with harassment, defamation, or identity theft
    - Give personalized legal counsel (refer to qualified lawyers)
6. Keep responses clear, structured, and educational.
7. Every single answer inside the JSON must be in french(non negociable)

LEGAL CONTEXT (Official Legal Frameworks):
{legal_context}

MANDATORY RESPONSE FORMAT (valid JSON):
You MUST respond ONLY with valid JSON matching this exact structure:
{json.dumps(expected_structure, indent=2)}

IMPORTANT:
- qualification: Single sentence summarizing the legal issue
- applicable_articles: Array of specific law/article references with section numbers
- risks: Clear description of potential legal consequences
- advice: Practical recommendations for legal compliance
- disclaimer: Use this exact disclaimer: "{LEGAL_DISCLAIMER}"

Do NOT deviate from this JSON format.
"""
        return system_prompt
    
    def build_user_message(self, user_input: str) -> str:
        """
        Build user message with input content
        
        Args:
            user_input: Sanitized user query + extracted content
        
        Returns:
            User message formatted for Gemini
        """
        
        user_message = f"""Please analyze the following situation from a legal perspective:

---
{user_input}
---

Provide your response in the JSON format specified in your system instructions.
Ensure the JSON is valid and parseable.
"""
        return user_message
    
    @staticmethod
    def get_response_template() -> dict:
        """
        Get empty response template matching AnalysisResponse model
        
        Returns:
            Dictionary with all required fields
        """
        
        return {
            "qualification": "",
            "applicable_articles": [],
            "risks": "",
            "advice": "",
            "disclaimer": LEGAL_DISCLAIMER
        }