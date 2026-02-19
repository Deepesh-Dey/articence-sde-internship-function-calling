
from typing import Any, List

from app.models.analytics import AnalyticsPoint
from app.models.crm import CRMCustomer
from app.models.support import SupportTicket


def identify_data_type(data: List[Any]) -> str:
    if not data:
        return "empty"

    first = data[0]

    # Handle typed Pydantic models
    if isinstance(first, AnalyticsPoint):
        return "time_series_analytics"
    if isinstance(first, SupportTicket):
        return "tabular_support"
    if isinstance(first, CRMCustomer):
        return "tabular_crm"

    # Fallback for plain dicts
    if isinstance(first, dict):
        if "date" in first and "metric" in first:
            return "time_series_analytics"
        if "ticket_id" in first:
            return "tabular_support"
        if "customer_id" in first:
            return "tabular_crm"

    return "unknown"

