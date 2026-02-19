
import json
from pathlib import Path
from typing import Any, List

from app.models.analytics import AnalyticsPoint

from .base import BaseConnector


class AnalyticsConnector(BaseConnector):
    """
    Connector for analytics / metrics data backed by a JSON file.
    """

    def fetch(self, **kwargs: Any) -> List[AnalyticsPoint]:
        path = Path("data") / "analytics.json"
        raw = json.loads(path.read_text())
        return [AnalyticsPoint.model_validate(item) for item in raw]

