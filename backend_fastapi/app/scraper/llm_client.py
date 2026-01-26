"""
Enhanced LLM Client (Groq API)
Safe-by-default, production-grade implementation
"""

import json
import re
from typing import Dict, Any, Tuple, Optional
import httpx
from app.core.config import settings


class LLMClient:
    """
    Enhanced LLM client using Groq API (cloud-based, lightweight)

    Guarantees:
    - NO .env required
    - NO crash if API key missing
    - Safe fallback if AI unavailable
    - JSON-only output
    """

    def __init__(self):
        # 🔒 API key may or may not exist (safe)
        self.groq_api_key: Optional[str] = settings.GROQ_API_KEY
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = settings.GROQ_MODEL
        self.max_content_length = 8000

    async def extract(
        self,
        content: str,
        prompt: str,
        schema: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], float]:

        # 🔒 AI disabled or no key → SAFE fallback
        if not self.groq_api_key:
            return self._fallback(schema)

        if len(content) > self.max_content_length:
            content = self._smart_truncate(content, self.max_content_length)

        full_prompt = self._build_prompt(content, prompt, schema)

        try:
            response = await self._call_llm(full_prompt)
            data = self._parse_json_response(response)

            if data:
                confidence = self._calculate_confidence(data, schema)
                return data, confidence

        except Exception:
            # Any failure → graceful fallback
            pass

        return self._fallback(schema)

    # ===================== GROQ CALL ===================== #

    async def _call_llm(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a precise data extraction engine. "
                        "Return ONLY valid JSON. No explanations."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.groq_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    # ===================== PROMPT ===================== #

    def _build_prompt(
        self,
        content: str,
        user_prompt: str,
        schema: Dict[str, Any]
    ) -> str:
        schema_description = self._describe_schema(schema)

        return f"""
You are an expert data extraction engine.

TASK:
{user_prompt}

EXPECTED SCHEMA:
{schema_description}

RULES:
- Output ONLY valid JSON
- Include all fields
- Use null for missing values
- Do NOT hallucinate

CONTENT:
---
{content}
---

JSON OUTPUT:
"""

    def _describe_schema(self, schema: Dict[str, Any]) -> str:
        lines = []
        for field, rules in schema.items():
            if isinstance(rules, dict):
                lines.append(
                    f"- {field}: {rules.get('type', 'string')} "
                    f"{'(required)' if rules.get('required', True) else '(optional)'}"
                )
            else:
                lines.append(f"- {field}: string")
        return "\n".join(lines)

    # ===================== JSON HANDLING ===================== #

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        response = response.strip()

        # Remove markdown blocks
        if response.startswith("```"):
            response = re.sub(r'^```(?:json)?\n?', '', response)
            response = re.sub(r'\n?```$', '', response)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON object
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Try repair
        repaired = self._repair_json(response)
        try:
            return json.loads(repaired)
        except Exception:
            return None

    def _repair_json(self, text: str) -> str:
        text = text.replace("'", '"')
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        text = re.sub(r'(\w+)(?=\s*:)', r'"\1"', text)
        return text

    # ===================== CONFIDENCE ===================== #

    def _calculate_confidence(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> float:
        filled = sum(
            1 for k in schema
            if data.get(k) not in [None, "", "null"]
        )
        base = filled / max(len(schema), 1)
        return round(min(1.0, base * self._assess_quality(data)), 2)

    def _assess_quality(self, data: Dict[str, Any]) -> float:
        score = 1.0
        for v in data.values():
            if isinstance(v, str) and len(v.strip()) < 2:
                score *= 0.8
        return score

    # ===================== FALLBACK ===================== #

    def _fallback(self, schema: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """
        Safe fallback when AI is unavailable
        """
        return {k: None for k in schema.keys()}, 0.25

    # ===================== UTILS ===================== #

    def _smart_truncate(self, content: str, max_length: int) -> str:
        if len(content) <= max_length:
            return content
        return (
            content[: int(max_length * 0.7)]
            + "\n...[truncated]...\n"
            + content[-int(max_length * 0.2):]
        )
