"""
LLM function/tool definitions for OpenAI and Anthropic APIs.
These schemas describe how an LLM can query the Universal Data Connector.
"""

from typing import Any

# Shared parameter definitions
COMMON_PARAMS = {
    "limit": {
        "type": "integer",
        "description": "Maximum number of results to return (1-50). Default 10. Use for voice: keep low.",
        "minimum": 1,
        "maximum": 50,
    },
    "offset": {
        "type": "integer",
        "description": "Number of results to skip for pagination. Ignored when voice=true.",
        "minimum": 0,
    },
    "voice": {
        "type": "boolean",
        "description": "When true, limits to 10 items for voice-optimized responses. Recommended for voice conversations.",
        "default": False,
    },
}

CRM_SPECIFIC_PARAMS = {
    "status": {
        "type": "string",
        "enum": ["active", "inactive"],
        "description": "Filter customers by status.",
    },
}

SUPPORT_SPECIFIC_PARAMS = {
    "status": {
        "type": "string",
        "enum": ["open", "closed"],
        "description": "Filter tickets by status.",
    },
    "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "Filter tickets by priority.",
    },
}

ANALYTICS_SPECIFIC_PARAMS = {
    "metric": {
        "type": "string",
        "description": "Filter by metric name (e.g. daily_active_users).",
    },
}


def _openai_tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    """Build a tool in OpenAI function-calling format."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }


def _anthropic_tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    """Build a tool in Anthropic input_schema format."""
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


def get_openai_tools() -> list[dict[str, Any]]:
    """Return tool definitions for OpenAI Chat Completions API (tools parameter)."""
    return [
        _openai_tool(
            name="get_crm_data",
            description="Retrieve customer CRM data. Use for questions about customers, accounts, or contact info.",
            properties={
                **COMMON_PARAMS,
                **CRM_SPECIFIC_PARAMS,
            },
            required=[],
        ),
        _openai_tool(
            name="get_support_tickets",
            description="Retrieve support tickets. Use for questions about open/closed tickets, issues, or customer support.",
            properties={
                **COMMON_PARAMS,
                **SUPPORT_SPECIFIC_PARAMS,
            },
            required=[],
        ),
        _openai_tool(
            name="get_analytics",
            description="Retrieve analytics and metrics. Use for questions about usage, daily active users, or performance metrics.",
            properties={
                **COMMON_PARAMS,
                **ANALYTICS_SPECIFIC_PARAMS,
            },
            required=[],
        ),
    ]


def get_anthropic_tools() -> list[dict[str, Any]]:
    """Return tool definitions for Anthropic Messages API (tools parameter)."""
    return [
        _anthropic_tool(
            name="get_crm_data",
            description="Retrieve customer CRM data. Use for questions about customers, accounts, or contact info.",
            properties={
                **COMMON_PARAMS,
                **CRM_SPECIFIC_PARAMS,
            },
            required=[],
        ),
        _anthropic_tool(
            name="get_support_tickets",
            description="Retrieve support tickets. Use for questions about open/closed tickets, issues, or customer support.",
            properties={
                **COMMON_PARAMS,
                **SUPPORT_SPECIFIC_PARAMS,
            },
            required=[],
        ),
        _anthropic_tool(
            name="get_analytics",
            description="Retrieve analytics and metrics. Use for questions about usage, daily active users, or performance metrics.",
            properties={
                **COMMON_PARAMS,
                **ANALYTICS_SPECIFIC_PARAMS,
            },
            required=[],
        ),
    ]


# Mapping from tool name to data source
TOOL_TO_SOURCE = {
    "get_crm_data": "crm",
    "get_support_tickets": "support",
    "get_analytics": "analytics",
}
