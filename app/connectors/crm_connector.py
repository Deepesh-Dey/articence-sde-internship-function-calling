import json
import logging
from pathlib import Path
from typing import Any, List

from app.models.crm import CRMCustomer

from .base import BaseConnector

logger = logging.getLogger(__name__)


class CRMConnector(BaseConnector):
    """
    Connector for CRM customer data backed by a JSON file.
    """

    def fetch(self, **kwargs: Any) -> List[CRMCustomer]:
        path = Path("data") / "customers.json"
        logger.info(f"Fetching CRM data from {path}")
        try:
            raw = json.loads(path.read_text())
            customers = [CRMCustomer.model_validate(item) for item in raw]
            logger.info(f"Successfully fetched {len(customers)} CRM customers")
            return customers
        except FileNotFoundError:
            logger.error(f"CRM data file not found: {path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse CRM JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching CRM data: {e}", exc_info=True)
            raise
