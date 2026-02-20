"""
✅ PRODUCTION-READY LLM TOOL SCHEMAS FOR ARTICENCE ASSIGNMENT
OpenAI + Anthropic function calling definitions for Universal Data Connector
"""

from typing import Any, Dict, List

# TOOL → DATA SOURCE MAPPING (used by llm.py)
TOOL_TO_SOURCE = {
    "get_crm_data": "crm",
    "get_support_tickets": "support", 
    "get_analytics": "analytics"
}

# Shared parameters across all tools
COMMON_PARAMS = {
    "limit": {
        "type": "integer",
        "description": "Max results (1-50). Voice mode: use 5-10.",
        "minimum": 1,
        "maximum": 50
    },
    "offset": {
        "type": "integer", 
        "description": "Skip results for pagination",
        "minimum": 0
    },
    "voice": {
        "type": "boolean",
        "description": "Voice-optimized (limits results, simple format)",
        "default": False
    }
}

# Tool-specific parameters
CRM_PARAMS = {
    "status": {
        "type": "string",
        "enum": ["active", "inactive"],
        "description": "Customer status filter"
    }
}

SUPPORT_PARAMS = {
    "status": {
        "type": "string", 
        "enum": ["open", "closed", "urgent"],
        "description": "Ticket status filter"
    },
    "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "Ticket priority filter"
    }
}

ANALYTICS_PARAMS = {
    "metric": {
        "type": "string",
        "description": "Metric name (churn, revenue, dau, etc.)"
    }
}

def _openai_tool(name: str, description: str, properties: Dict[str, Any], required: List[str] = None) -> Dict[str, Any]:
    """OpenAI Chat Completions tools format"""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
                "additionalProperties": False
            }
        }
    }

def _anthropic_tool(name: str, description: str, properties: Dict[str, Any], required: List[str] = None) -> Dict[str, Any]:
    """Anthropic Messages API tools format"""
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required or []
        }
    }

def get_openai_tools() -> List[Dict[str, Any]]:
    """🎯 OPENAI FUNCTION CALLING - Copy these exact schemas to your LLM client"""
    return [
        # 🛒 CRM Data
        _openai_tool(
            name="get_crm_data",
            description="Get customer profiles, accounts, purchase history. Use for customer questions.",
            properties={
                **COMMON_PARAMS,
                **CRM_PARAMS,
                "customer_id": {"type": "string", "description": "Specific customer ID"}
            },
            required=["limit"]
        ),
        
        # 🎫 Support Tickets  
        _openai_tool(
            name="get_support_tickets",
            description="Get support tickets by status/priority. Use for issue tracking questions.",
            properties={
                **COMMON_PARAMS,
                **SUPPORT_PARAMS
            },
            required=["limit"]
        ),
        
        # 📈 Analytics Metrics
        _openai_tool(
            name="get_analytics",
            description="Get business metrics (churn, revenue, DAU). Use for performance questions.",
            properties={
                **COMMON_PARAMS,
                **ANALYTICS_PARAMS
            },
            required=["limit"]
        )
    ]

def get_anthropic_tools() -> List[Dict[str, Any]]:
    """🎯 ANTHROPIC TOOL USE - Same tools, Anthropic format"""
    openai_tools = get_openai_tools()
    return [
        _anthropic_tool(
            tool["function"]["name"],
            tool["function"]["description"], 
            tool["function"]["parameters"]["properties"],
            tool["function"]["parameters"]["required"]
        ) for tool in openai_tools
    ]
