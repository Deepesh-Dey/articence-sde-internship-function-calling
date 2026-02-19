from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class AnalyticsPoint(BaseModel):
    metric: str
    date: date
    value: int

