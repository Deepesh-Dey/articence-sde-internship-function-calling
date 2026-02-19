import json
import logging
from pathlib import Path
from typing import Any, List

from app.models.analytics import AnalyticsPoint

from .base import BaseConnector

logger = logging.getLogger(__name__)


class AnalyticsConnector(BaseConnector):
    """
    Connector for analytics / metrics data backed by a JSON file.
    """

    def fetch(self, **kwargs: Any) -> List[AnalyticsPoint]:
        path = Path("data") / "analytics.json"
        logger.info(f"Fetching analytics data from {path}")
        try:
            raw = json.loads(path.read_text())
            points = [AnalyticsPoint.model_validate(item) for item in raw]
            logger.info(f"Successfully fetched {len(points)} analytics points")
            return points
        except FileNotFoundError:
            logger.error(f"Analytics data file not found: {path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analytics JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching analytics data: {e}", exc_info=True)
            raise
