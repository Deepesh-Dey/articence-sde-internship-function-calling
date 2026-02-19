import logging

from fastapi import APIRouter, Query

from app.config import settings
from app.models.common import DataResponse
from app.services.data_service import fetch_data

logger = logging.getLogger(__name__)

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
):
    logger.info(f"GET /data/{source} - limit={limit}, offset={offset}, voice={voice}")
    return fetch_data(
        source,
        limit=limit,
        offset=offset,
        status=status,
        priority=priority,
        metric=metric,
        voice=voice,
    )
