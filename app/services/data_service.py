"""
Unified data fetching service used by REST and LLM endpoints.
"""

import logging

from app.connectors.analytics_connector import AnalyticsConnector
from app.connectors.crm_connector import CRMConnector
from app.connectors.support_connector import SupportConnector
from app.config import settings
from app.models.common import DataResponse, Metadata
from app.services.business_rules import apply_filters, apply_pagination, prioritize_recent
from app.services.data_identifier import identify_data_type
from app.services.voice_optimizer import get_context_message, get_freshness_message, summarize_if_large

logger = logging.getLogger(__name__)

CONNECTOR_MAP = {
    "crm": CRMConnector(),
    "support": SupportConnector(),
    "analytics": AnalyticsConnector(),
}


def fetch_data(
    source: str,
    *,
    limit: int | None = None,
    offset: int = 0,
    status: str | None = None,
    priority: str | None = None,
    metric: str | None = None,
    voice: bool = False,
) -> DataResponse:
    """
    Fetch, filter, and optimize data from the specified source.
    """
    logger.info(
        f"Fetching data from source={source}, limit={limit}, offset={offset}, "
        f"status={status}, priority={priority}, metric={metric}, voice={voice}"
    )
    
    connector = CONNECTOR_MAP.get(source)
    if not connector:
        logger.warning(f"Unknown data source: {source}")
        return DataResponse(
            data=[],
            metadata=Metadata(
                total_results=0,
                returned_results=0,
                data_freshness="unknown",
                data_type="unknown",
                source=source,
                context_message="No results",
            ),
        )

    raw_data = connector.fetch()
    data_type = identify_data_type(raw_data)
    logger.debug(f"Identified data type: {data_type}, raw count: {len(raw_data)}")

    filtered = apply_filters(
        raw_data,
        status=status,
        priority=priority,
        metric=metric,
    )
    total_after_filter = len(filtered)
    filtered = prioritize_recent(filtered)

    optimized = summarize_if_large(filtered, data_type)
    is_summarized = (
        len(optimized) == 1
        and isinstance(optimized[0], dict)
        and optimized[0].get("type") == "aggregated"
    )

    if is_summarized:
        logger.info("Returning aggregated summary for large analytics dataset")
        final_data = optimized
        returned_count = 1
    else:
        effective_limit = settings.MAX_RESULTS if voice else (limit or settings.DEFAULT_PAGE_SIZE)
        effective_offset = 0 if voice else offset
        paginated = apply_pagination(filtered, offset=effective_offset, limit=effective_limit)
        final_data = paginated
        returned_count = len(paginated)

    context_msg = get_context_message(returned_count, total_after_filter)
    voice_summary = None
    if voice and total_after_filter > 0:
        if data_type == "tabular_crm":
            voice_summary = f"{total_after_filter} customers. {context_msg}"
        elif data_type == "tabular_support":
            voice_summary = f"{total_after_filter} tickets. {context_msg}"
        elif data_type == "time_series_analytics" and is_summarized:
            agg = optimized[0]
            voice_summary = agg.get("summary", str(agg))
        else:
            voice_summary = f"{context_msg}. {get_freshness_message()}"

    metadata = Metadata(
        total_results=total_after_filter,
        returned_results=returned_count,
        data_freshness=get_freshness_message(),
        data_type=data_type,
        source=source,
        context_message=context_msg,
        voice_summary=voice_summary,
    )

    logger.info(
        f"Data fetch complete: source={source}, returned={returned_count}/{total_after_filter}, "
        f"type={data_type}, voice={voice}"
    )
    return DataResponse(data=final_data, metadata=metadata)
