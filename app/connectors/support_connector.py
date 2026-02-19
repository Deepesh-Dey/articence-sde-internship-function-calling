
import json
from pathlib import Path
from typing import Any, List

from app.models.support import SupportTicket

from .base import BaseConnector


class SupportConnector(BaseConnector):
    """
    Connector for support ticket data backed by a JSON file.
    """

    def fetch(self, **kwargs: Any) -> List[SupportTicket]:
        path = Path("data") / "support_tickets.json"
        raw = json.loads(path.read_text())
        return [SupportTicket.model_validate(item) for item in raw]

