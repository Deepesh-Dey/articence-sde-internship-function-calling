"""
Business rules engine for the Universal Data Connector.
Applies voice-optimized limits, prioritization, and filtering.
"""

import logging
from typing import Any, List, Optional

from app.config import settings
from app.models.analytics import AnalyticsPoint
from app.models.crm import CRMCustomer
from app.models.support import SupportTicket

logger = logging.getLogger(__name__)


def _sort_key(item: Any) -> Any:
    """Return value for recency ordering (newest first)."""
    if hasattr(item, "created_at"):
        return item.created_at
    if hasattr(item, "date"):
        return item.date
    return ""


def prioritize_recent(data: List[Any]) -> List[Any]:
    """
    Sort data by most recent first.
    Prioritization rule: return most recent/relevant first for voice.
    """
    if not data:
        return data
    logger.debug(f"Prioritizing {len(data)} items by recency")
    return sorted(data, key=_sort_key, reverse=True)


def apply_filters(
    data: List[Any],
    *,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    metric: Optional[str] = None,
) -> List[Any]:
    """
    Apply optional filters based on data structure.
    CRM: status (active/inactive)
    Support: status (open/closed), priority (low/medium/high)
    Analytics: metric name
    """
    if not status and not priority and not metric:
        return data

    filters = []
    if status:
        filters.append(f"status={status}")
    if priority:
        filters.append(f"priority={priority}")
    if metric:
        filters.append(f"metric={metric}")
    logger.info(f"Applying filters: {', '.join(filters)} to {len(data)} items")

    result: List[Any] = []
    for item in data:
        if isinstance(item, CRMCustomer):
            if status and item.status != status:
                continue
        elif isinstance(item, SupportTicket):
            if status and item.status != status:
                continue
            if priority and item.priority != priority:
                continue
        elif isinstance(item, AnalyticsPoint):
            if metric and item.metric != metric:
                continue
        elif isinstance(item, dict):
            if status and item.get("status") != status:
                continue
            if priority and item.get("priority") != priority:
                continue
            if metric and item.get("metric") != metric:
                continue
        result.append(item)
    
    logger.info(f"Filtered {len(data)} items to {len(result)} items")
    return result


def apply_voice_limits(data: List[Any], limit: Optional[int] = None) -> List[Any]:
    """
    Limit results for voice context.
    Default max 10 items for voice conversations.
    """
    max_items = limit if limit is not None else settings.MAX_RESULTS
    capped = min(max_items, settings.MAX_PAGE_SIZE)
    if len(data) > capped:
        logger.info(f"Limiting {len(data)} items to {capped} for voice context")
    return data[:capped]


def apply_pagination(
    data: List[Any],
    offset: int = 0,
    limit: Optional[int] = None,
) -> List[Any]:
    """Apply offset and limit for pagination."""
    max_items = limit if limit is not None else settings.DEFAULT_PAGE_SIZE
    capped = min(max_items, settings.MAX_PAGE_SIZE)
    start = max(0, offset)
    end = start + capped
    logger.debug(f"Paginating: offset={offset}, limit={capped}, returning items {start}-{end} of {len(data)}")
    return data[start:end]
