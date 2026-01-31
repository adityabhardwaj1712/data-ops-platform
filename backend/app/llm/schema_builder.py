import logging
import json
from typing import Dict, Any, Optional
from app.scraper.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

class AISchemaBuilder:
    """
    Converts natural language descriptions into structured JSON schemas for scraping.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    async def build(self, prompt: str) -> Dict[str, Any]:
        """
        Takes a string like "product name, price, and specs" and returns a JSON schema.
        """
        system_prompt = (
            "You are a scraping schema expert. Convert natural language extraction requests "
            "into a flat JSON object where keys are field names and values are CSS selectors or descriptions. "
            "Example: 'Title and price' -> {'title': 'h1', 'price': '.price'} "
            "Return ONLY a raw JSON object, no markdown, no explanation."
        )
        
        try:
            # Note: Using generic extraction prompt logic or direct LLM call
            # For now, we'll use a direct prompt to the LLM
            user_prompt = f"Create a scraping schema for: {prompt}"
            
            # This is a placeholder for where we'd call the LLM to get the schema
            # Since LLMClient.extract is for data extraction, we might need a meta-prompt
            raw_response = await self.llm_client.generate_schema(user_prompt, system_prompt)
            
            return json.loads(raw_response)
        except Exception as e:
            logger.error(f"AI Schema Builder failed: {e}")
            # Fallback to a very basic title extraction if LLM fails
            return {"title": "title"}

    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """Simple validation to ensure it's a flat dictionary."""
        if not isinstance(schema, dict):
            return False
        return all(isinstance(k, str) for k in schema.keys())
