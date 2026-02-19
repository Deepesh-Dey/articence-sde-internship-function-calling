"""Hugging Face LLM analysis router."""

import json
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.data_service import fetch_data
from app.services.huggingface_service import analyze_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["Analysis"])


class AnalyzeRequest(BaseModel):
    query: str
    source: str | None = None
    model_type: str = "auto"  # summarization | table_qa | text_qa | auto


@router.post("")
async def analyze(request: AnalyzeRequest):
    """
    Get analysis from Hugging Face models.
    Models: summarization (MEETING_SUMMARY), table_qa (tapas), text_qa (flan-t5).
    """
    sources = [request.source] if request.source else ["crm", "support", "analytics"]
    all_data = {}
    for src in sources:
        try:
            result = fetch_data(src, limit=50, voice=False)
            if result.data:
                all_data[src] = result.data
        except Exception as e:
            logger.warning("Could not fetch %s: %s", src, e)

    if not all_data:
        raise HTTPException(status_code=400, detail="No data available. Upload data first.")

    def to_serializable(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump(mode="json")
        if hasattr(obj, "dict"):
            d = obj.dict()
            for k, v in list(d.items()):
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
            return d
        return obj

    serialized = {
        k: [to_serializable(item) for item in v[:30]]
        for k, v in all_data.items()
    }
    data_context = json.dumps(serialized)

    try:
        analysis = analyze_data(request.query, data_context, request.model_type)
        return {"analysis": analysis, "sources_used": list(all_data.keys())}
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Hugging Face analysis failed")
        raise HTTPException(status_code=500, detail=str(e))
