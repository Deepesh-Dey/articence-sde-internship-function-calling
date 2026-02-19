from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


CRMStatus = Literal["active", "inactive"]


class CRMCustomer(BaseModel):
    customer_id: int
    name: str
    email: str
    created_at: datetime
    status: CRMStatus

