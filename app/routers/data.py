from datetime import datetime

from fastapi import APIRouter, Query

from app.connectors.analytics_connector import AnalyticsConnector
from app.connectors.crm_connector import CRMConnector
from app.connectors.support_connector import SupportConnector
from app.config import settings
from app.models.common import DataResponse, Metadata
from app.services.business_rules import (
    apply_filters,
    apply_pagination,
    prioritize_recent,
)
from app.services.data_identifier import identify_data_type
from app.services.voice_optimizer import get_context_message, get_freshness_message, summarize_if_large


router = APIRouter()


@router.get("/data/{source}", response_model=DataResponse)
def get_data(
    source: str,
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=50),
    offset: int = Query(0, ge=0),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    metric: str | None = Query(None),
    voice: bool = Query(False, description="Apply voice optimizations (max 10 items)"),
) -> DataResponse:
    connector_map = {
        "crm": CRMConnector(),
        "support": SupportConnector(),
        "analytics": AnalyticsConnector(),
    }

    connector = connector_map.get(source)
    if not connector:
        empty_metadata = Metadata(
            total_results=0,
            returned_results=0,
            data_freshness="unknown",
            data_type="unknown",
            source=source,
            context_message="No results",
        )
        return DataResponse(data=[], metadata=empty_metadata)

    raw_data = connector.fetch()
    data_type = identify_data_type(raw_data)

    # 1. Filter
    filtered = apply_filters(
        raw_data,
        status=status,
        priority=priority,
        metric=metric,
    )
    total_after_filter = len(filtered)

    # 2. Prioritize by recency
    filtered = prioritize_recent(filtered)

    # 3. Summarize large analytics for voice
    optimized = summarize_if_large(filtered, data_type)
    is_summarized = len(optimized) == 1 and isinstance(optimized[0], dict) and optimized[0].get("type") == "aggregated"

    # 4. Pagination / voice limits
    if is_summarized:
        final_data = optimized
        returned_count = 1
    else:
        effective_limit = settings.MAX_RESULTS if voice else limit
        effective_offset = 0 if voice else offset
        paginated = apply_pagination(filtered, offset=effective_offset, limit=effective_limit)
        final_data = paginated
        returned_count = len(paginated)

    # 5. Build metadata
    context_msg = get_context_message(returned_count, total_after_filter)
    metadata = Metadata(
        total_results=total_after_filter,
        returned_results=returned_count,
        data_freshness=get_freshness_message(),
        data_type=data_type,
        source=source,
        context_message=context_msg,
    )

    return DataResponse(data=final_data, metadata=metadata)
