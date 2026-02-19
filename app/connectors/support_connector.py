import json
import logging
from pathlib import Path
from typing import Any, List

from app.models.support import SupportTicket

from .base import BaseConnector

logger = logging.getLogger(__name__)


class SupportConnector(BaseConnector):
    """
    Connector for support ticket data backed by a JSON file.
    """

    def fetch(self, **kwargs: Any) -> List[SupportTicket]:
        path = Path("data") / "support_tickets.json"
        logger.info(f"Fetching support tickets from {path}")
        try:
            raw = json.loads(path.read_text())
            tickets = [SupportTicket.model_validate(item) for item in raw]
            logger.info(f"Successfully fetched {len(tickets)} support tickets")
            return tickets
        except FileNotFoundError:
            logger.error(f"Support tickets file not found: {path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse support tickets JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching support tickets: {e}", exc_info=True)
            raise
