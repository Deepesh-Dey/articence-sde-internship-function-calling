from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.routers.llm import execute_tool_call

router = APIRouter(prefix="/query", tags=["🎤 Voice Query"])

class VoiceQuery(BaseModel):
    query: str

@router.post("/")
async def voice_to_data(query: VoiceQuery):
    """Voice → LLM Tool Selection → Data"""
    q = query.query.lower()
    
    if "churn" in q or "revenue" in q:
        tool, args = "get_analytics", {"limit": 10}
    elif "customer" in q:
        tool, args = "get_crm_data", {"limit": 5}
    elif "ticket" in q or "support" in q:
        tool, args = "get_support_tickets", {"status": "open"}
    else:
        return {"error": "Try: 'churn rate' or 'support tickets'"}
    
    request = type('obj', (object,), {'tool': tool, 'arguments': args})()
    result = execute_tool_call(request)
    
    return {
        "voice_query": query.query,
        "tool_used": tool,
        "results": len(result.get('data', [])),
        "data": result
    }
