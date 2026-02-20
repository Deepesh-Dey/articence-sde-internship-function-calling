"""
LLM integration endpoints for function/tool calling.
PRODUCTION READY - OpenAI + Anthropic compatible.
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from app.models.llm import LLMToolCallRequest
from app.schemas.llm_tools import get_anthropic_tools, get_openai_tools

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm", tags=["LLM Integration"])

# TOOL MAPPING - FIXED CIRCULAR IMPORT
TOOL_TO_SOURCE = {
    "get_crm_data": "crm",
    "get_support_tickets": "support", 
    "get_analytics": "analytics",
}

@router.get("/tools")
def get_tools(
    provider: str = Query("openai", description="openai or anthropic"),
):
    """
    Return tool definitions for LLM function calling.
    Use these in the tools parameter when calling OpenAI or Anthropic APIs.
    """
    logger.info(f"GET /llm/tools - provider={provider}")
    provider_lower = provider.lower()
    
    if provider_lower == "openai":
        tools = get_openai_tools()
        logger.debug(f"Returning {len(tools)} OpenAI tools")
        return {"tools": tools}
    elif provider_lower == "anthropic":
        tools = get_anthropic_tools()
        logger.debug(f"Returning {len(tools)} Anthropic tools")
        return {"tools": tools}
    else:
        logger.warning(f"Invalid provider requested: {provider}")
        raise HTTPException(status_code=400, detail="provider must be 'openai' or 'anthropic'")

@router.post("/query")
def execute_tool_call(request: LLMToolCallRequest):
    """
    Execute a tool call from an LLM and return data.
    Call this when your LLM returns a tool_use block; pass the tool name and arguments here.
    """
    from app.services.data_service import fetch_data

    logger.info(f"POST /llm/query - tool={request.tool}, arguments={request.arguments}")
    
    source = TOOL_TO_SOURCE.get(request.tool)
    if not source:
        logger.warning(f"Unknown tool requested: {request.tool}")
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tool: {request.tool}. Available: {list(TOOL_TO_SOURCE.keys())}",
        )

    args = request.arguments or {}
    result = fetch_data(
        source,
        limit=args.get("limit"),
        offset=args.get("offset", 0),
        status=args.get("status"),
        priority=args.get("priority"),
        metric=args.get("metric"),
        voice=args.get("voice", False),
    )
    
    logger.info(f"Tool call success: {request.tool} → {result.metadata.returned_results} items from {source}")
    return result

@router.get("/health")
def llm_health():
    """Health check for LLM integration"""
    return {
        "status": "healthy",
        "tools": list(TOOL_TO_SOURCE.keys()),
        "providers": ["openai", "anthropic"],
        "data_sources": list(TOOL_TO_SOURCE.values())
    }
