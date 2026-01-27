"""
Groq AI Integration (FREE, OPTIONAL)
Safe, lazy-loaded AI client that NEVER crashes the app
"""

import logging
from typing import Dict, Any, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqAI:
    """
    Safe Groq AI wrapper.

    - Groq SDK is OPTIONAL
    - API key is OPTIONAL
    - App never crashes if AI is unavailable
    """

    def __init__(self):
        self._client = None
        self.model = settings.GROQ_MODEL

    # =====================================================
    # INTERNAL: Lazy client loader
    # =====================================================
    def _get_client(self):
        if not settings.ENABLE_AI_COPILOT:
            return None

        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set – AI disabled")
            return None

        if self._client is not None:
            return self._client

        try:
            from groq import Groq  # 🔥 lazy import (CRITICAL)
            self._client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info("Groq AI client initialized")
            return self._client
        except ImportError:
            logger.error("Groq SDK not installed (pip install groq)")
            return None
        except Exception as e:
            logger.error(f"Failed to init Groq client: {e}")
            return None

    # =====================================================
    # INTERNAL: Chat helper
    # =====================================================
    async def _chat(self, prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str:
        client = self._get_client()
        if not client:
            return "AI is currently unavailable"

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq AI error: {e}")
            return "AI request failed"

    # =====================================================
    # PUBLIC METHODS (USED BY API)
    # =====================================================
    async def explain_dataset(self, dataset_summary: Dict[str, Any]) -> str:
        prompt = f"""
Explain this dataset in simple terms.

Dataset summary:
{dataset_summary}

Keep it short and clear.
"""
        return await self._chat(prompt, max_tokens=200)

    async def detect_schema(self, sample_data: List[Dict[str, Any]]) -> Dict[str, str]:
        prompt = f"""
Infer a schema from this sample data.

Sample:
{sample_data[:3]}

Return ONLY valid JSON:
{{"field": "type"}}
"""
        response = await self._chat(prompt, max_tokens=300, temperature=0.3)

        try:
            import json
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except Exception as e:
            logger.error(f"Schema parse error: {e}")

        return {}

    async def analyze_change(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> str:
        prompt = f"""
Analyze the change between datasets.

OLD:
{old_data}

NEW:
{new_data}

Explain what changed and why.
"""
        return await self._chat(prompt, max_tokens=250)

    async def answer_query(self, query: str, context: Dict[str, Any]) -> str:
        prompt = f"""
Answer the question based on this dataset.

QUESTION:
{query}

CONTEXT:
{context}
"""
        return await self._chat(prompt, max_tokens=200)


# =====================================================
# SAFE GLOBAL INSTANCE
# =====================================================
groq_ai = GroqAI()

