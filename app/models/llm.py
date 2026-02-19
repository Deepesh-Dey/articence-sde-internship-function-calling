"""Request/response models for LLM integration."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class LLMToolCallRequest(BaseModel):
    """Request body for executing an LLM tool call."""

    tool: str = Field(
        ...,
        description="Tool name: get_crm_data, get_support_tickets, or get_analytics",
    )
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments from the LLM's tool call (e.g. status, priority, voice)",
    )
