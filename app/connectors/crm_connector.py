
import json
from pathlib import Path
from typing import Any, List

from app.models.crm import CRMCustomer

from .base import BaseConnector


class CRMConnector(BaseConnector):
    """
    Connector for CRM customer data backed by a JSON file.
    """

    def fetch(self, **kwargs: Any) -> List[CRMCustomer]:
        path = Path("data") / "customers.json"
        raw = json.loads(path.read_text())
        return [CRMCustomer.model_validate(item) for item in raw]

