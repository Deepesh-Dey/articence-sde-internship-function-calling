from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


TicketPriority = Literal["low", "medium", "high"]
TicketStatus = Literal["open", "closed"]


class SupportTicket(BaseModel):
    ticket_id: int
    customer_id: int
    subject: str
    priority: TicketPriority
    created_at: datetime
    status: TicketStatus

