"""
LLM integration endpoints for function/tool calling.
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.models.llm import LLMToolCallRequest
from app.schemas.llm_tools import TOOL_TO_SOURCE, get_anthropic_tools, get_openai_tools

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM Integration"])


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
    if provider_lower == "anthropic":
        tools = get_anthropic_tools()
        logger.debug(f"Returning {len(tools)} Anthropic tools")
        return {"tools": tools}
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
            detail=f"Unknown tool: {request.tool}. Use get_crm_data, get_support_tickets, or get_analytics.",
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
    logger.info(f"Tool call completed: tool={request.tool}, returned={result.metadata.returned_results} items")
    return result
