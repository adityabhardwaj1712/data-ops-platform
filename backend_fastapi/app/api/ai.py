"""
AI API Endpoints (FREE via Groq)
Safe, optional AI copilot features
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from app.core.config import settings
from app.ai.groq_client import groq_ai

router = APIRouter(prefix="/ai", tags=["AI"])


# =========================
# REQUEST MODELS
# =========================

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


# =========================
# ENDPOINTS
# =========================

@router.post("/explain")
async def explain_dataset(request: ExplainRequest):
    if not settings.ENABLE_AI_COPILOT:
        raise HTTPException(status_code=403, detail="AI Copilot disabled")

    try:
        return {
            "explanation": await groq_ai.explain_dataset(request.summary)
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/schema")
async def detect_schema(request: SchemaRequest):
    if not settings.ENABLE_AI_COPILOT:
        raise HTTPException(status_code=403, detail="AI Copilot disabled")

    try:
        return await groq_ai.detect_schema(request.sample_data)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/change-analysis")
async def analyze_change(request: ChangeAnalysisRequest):
    if not settings.ENABLE_AI_COPILOT:
        raise HTTPException(status_code=403, detail="AI Copilot disabled")

    try:
        return {
            "analysis": await groq_ai.analyze_change(
                request.old_data,
                request.new_data,
            )
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/query")
async def answer_query(request: QueryRequest):
    if not settings.ENABLE_AI_COPILOT:
        raise HTTPException(status_code=403, detail="AI Copilot disabled")

    try:
        return {
            "answer": await groq_ai.answer_query(
                request.query,
                request.context,
            )
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

