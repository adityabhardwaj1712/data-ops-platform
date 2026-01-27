"""
Groq AI Integration (FREE)
Fast, free LLM inference for AI features
"""

import os
import logging
from typing import Dict, Any, List, Optional
from groq import Groq

logger = logging.getLogger(__name__)


class GroqAI:
    """
    Free AI using Groq API.
    
    Features:
    - Dataset explanation
    - Schema detection
    - Change intelligence
    - Root-cause analysis
    - Query answering
    
    Cost: FREE (Groq API is free)
    Speed: 500+ tokens/sec
    """
    
    def __init__(self):
        self._client = None
        self.model = "llama-3.1-70b-versatile"  # Free model
    
    def _get_client(self):
        """Lazy-load Groq client."""
        if self._client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                logger.warning("GROQ_API_KEY not set. AI features disabled.")
                return None
            
            self._client = Groq(api_key=api_key)
            logger.info("Groq AI client initialized")
        
        return self._client
    
    async def explain_dataset(self, dataset_summary: Dict[str, Any]) -> str:
        """
        Explain dataset in natural language.
        
        Args:
            dataset_summary: Dataset metadata (row count, fields, etc.)
        
        Returns:
            Natural language explanation
        """
        client = self._get_client()
        if not client:
            return "AI features not available (GROQ_API_KEY not set)"
        
        prompt = f"""Explain this dataset in simple terms:
        
Dataset Summary:
- Total rows: {dataset_summary.get('row_count', 0)}
- Fields: {', '.join(dataset_summary.get('fields', []))}
- Confidence: {dataset_summary.get('avg_confidence', 0):.0%}
- Last updated: {dataset_summary.get('last_updated', 'Unknown')}

Provide a brief, clear explanation."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Groq AI error: {e}")
            return f"AI explanation unavailable: {str(e)}"
    
    async def detect_schema(self, sample_data: List[Dict]) -> Dict[str, str]:
        """
        AI-powered schema detection.
        
        Args:
            sample_data: Sample rows from dataset
        
        Returns:
            Inferred schema {field: type}
        """
        client = self._get_client()
        if not client:
            return {}
        
        prompt = f"""Analyze this data and infer the schema.
        
Sample data (first 3 rows):
{sample_data[:3]}

Return ONLY a JSON object mapping field names to types (string, number, boolean, date, email, url, etc.).
Example: {{"name": "string", "age": "number", "email": "email"}}"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse JSON response
            import json
            schema_text = response.choices[0].message.content
            # Extract JSON from response
            start = schema_text.find('{')
            end = schema_text.rfind('}') + 1
            if start >= 0 and end > start:
                schema = json.loads(schema_text[start:end])
                return schema
            
            return {}
        
        except Exception as e:
            logger.error(f"Schema detection error: {e}")
            return {}
    
    async def analyze_change(self, old_data: Dict, new_data: Dict) -> str:
        """
        Explain what changed and why it might have changed.
        
        Args:
            old_data: Previous data
            new_data: Current data
        
        Returns:
            Change analysis
        """
        client = self._get_client()
        if not client:
            return "AI analysis not available"
        
        prompt = f"""Analyze what changed between these two datasets:

OLD DATA:
{old_data}

NEW DATA:
{new_data}

Explain:
1. What changed (be specific)
2. Why it might have changed (possible reasons)
3. Is this change significant?

Keep it concise (2-3 sentences)."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=250
            )
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Change analysis error: {e}")
            return f"Analysis unavailable: {str(e)}"
    
    async def root_cause_analysis(self, error: str, context: Dict) -> str:
        """
        Diagnose why a job failed and suggest fixes.
        
        Args:
            error: Error message
            context: Job context (URL, strategy, etc.)
        
        Returns:
            Diagnosis and fix suggestions
        """
        client = self._get_client()
        if not client:
            return "AI diagnosis not available"
        
        prompt = f"""A scraping job failed. Help diagnose the issue:

ERROR: {error}

CONTEXT:
- URL: {context.get('url', 'Unknown')}
- Strategy: {context.get('strategy', 'Unknown')}
- Retry count: {context.get('retries', 0)}

Provide:
1. Most likely cause
2. Recommended fix
3. Alternative solutions

Be concise and actionable."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Root cause analysis error: {e}")
            return f"Diagnosis unavailable: {str(e)}"
    
    async def answer_query(self, query: str, dataset_context: Dict) -> str:
        """
        Answer natural language questions about a dataset.
        
        Args:
            query: User question
            dataset_context: Dataset information
        
        Returns:
            Answer
        """
        client = self._get_client()
        if not client:
            return "AI query answering not available"
        
        prompt = f"""Answer this question about a dataset:

QUESTION: {query}

DATASET INFO:
{dataset_context}

Provide a clear, concise answer based on the available data."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Query answering error: {e}")
            return f"Answer unavailable: {str(e)}"


# Global Groq AI instance
groq_ai = GroqAI()
