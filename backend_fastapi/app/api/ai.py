"""
AI API Endpoints (FREE via Groq)
Expose AI copilot and analysis features
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.core.config import settings
from app.ai.groq_client import groq_ai

router = APIRouter()


class ExplainRequest(BaseModel):
    summary: Dict[str, Any]


class SchemaRequest(BaseModel):
    sample_data: List[Dict[str, Any]]


class ChangeAnalysisRequest(BaseModel):
    old_data: Dict[str, Any]
    new_data: Dict[str, Any]


class QueryRequest(BaseModel):
    query: str
    context: Dict[str, Any]


@router.post("/explain")
async def explain_dataset(request: ExplainRequest):
    """Explain dataset using AI."""
    if not settings.ENABLE_AI_COPILOT:
        raise HTTPException(status_code=403, detail="AI Copilot disabled")
    
    return {"explanation": await groq_ai.explain_dataset(request.summary)}


@router.post("/schema")
async def detect_schema(request: SchemaRequest):
    """Detect schema from sample data."""
    if not settings.ENABLE_AI_COPILOT:
        raise HTTPException(status_code=403, detail="AI Copilot disabled")
    
    return {"schema": await groq_ai.detect_schema(request.sample_data)}


@router.post("/change-analysis")
async def analyze_change(request: ChangeAnalysisRequest):
    """Analyze changes between two datasets."""
    if not settings.ENABLE_AI_COPILOT:
        raise HTTPException(status_code=403, detail="AI Copilot disabled")
    
    return {"analysis": await groq_ai.analyze_change(request.old_data, request.new_data)}


@router.post("/query")
async def answer_query(request: QueryRequest):
    """Answer natural language query about data."""
    if not settings.ENABLE_AI_COPILOT:
        raise HTTPException(status_code=403, detail="AI Copilot disabled")
    
    return {"answer": await groq_ai.answer_query(request.query, request.context)}
