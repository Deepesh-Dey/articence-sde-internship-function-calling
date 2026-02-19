"""
Voice-specific optimizations for the Universal Data Connector.
Summarization and context messages for voice conversations.
"""

from datetime import UTC, datetime
from typing import Any, Dict, List

from app.models.analytics import AnalyticsPoint

# Threshold above which we aggregate analytics instead of returning raw points
ANALYTICS_AGGREGATION_THRESHOLD = 20


def aggregate_analytics(data: List[Any]) -> Dict[str, Any]:
    """
    Aggregate time-series analytics into summary stats.
    Used when dataset is large to keep voice responses concise.
    """
    if not data:
        return {"summary": "No data", "count": 0}

    values = []
    metric_name = ""
    for item in data:
        if isinstance(item, AnalyticsPoint):
            values.append(item.value)
            metric_name = item.metric
        elif isinstance(item, dict) and "value" in item:
            values.append(item["value"])
            metric_name = item.get("metric", "metric")

    if not values:
        return {"summary": "No values", "count": 0}

    return {
        "type": "aggregated",
        "metric": metric_name,
        "count": len(values),
        "avg": round(sum(values) / len(values), 1),
        "min": min(values),
        "max": max(values),
        "summary": f"{metric_name}: {len(values)} data points, avg {round(sum(values)/len(values), 1)}, range {min(values)}-{max(values)}",
    }


def summarize_if_large(
    data: List[Any],
    data_type: str,
) -> List[Any]:
    """
    For large analytics datasets, return aggregated summary instead of raw data.
    For tabular data (CRM, support), always return items - never replace with summary.
    """
    if data_type == "time_series_analytics" and len(data) > ANALYTICS_AGGREGATION_THRESHOLD:
        agg = aggregate_analytics(data)
        return [agg]
    return data


def get_context_message(returned: int, total: int) -> str:
    """
    Voice-friendly context: "Showing X of Y results".
    """
    if total == 0:
        return "No results"
    if returned >= total:
        return f"Showing all {total} results"
    return f"Showing {returned} of {total} results"


def get_freshness_message(updated_at: datetime | None = None) -> str:
    """
    Human-readable freshness indicator for voice.
    """
    if updated_at:
        delta = datetime.now(UTC) - updated_at
        hours = delta.total_seconds() / 3600
        if hours < 1:
            return "Data as of a few minutes ago"
        if hours < 24:
            return f"Data as of {int(hours)} hours ago"
        return f"Data as of {int(hours / 24)} days ago"
    return f"Data as of {datetime.now(UTC).isoformat()}"
