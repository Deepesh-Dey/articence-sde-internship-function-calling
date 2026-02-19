from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from random import choice, randint
from typing import Any, Dict, Iterable, List, Sequence


def generate_customers(count: int = 50) -> List[Dict[str, Any]]:
    now = datetime.now(UTC)
    customers: List[Dict[str, Any]] = []
    for i in range(1, count + 1):
        created_at = now - timedelta(days=randint(0, 365))
        customers.append(
            {
                "customer_id": i,
                "name": f"Customer {i}",
                "email": f"user{i}@example.com",
                "created_at": created_at.isoformat(),
                "status": choice(["active", "inactive"]),
            }
        )
    return customers


def generate_support_tickets(
    count: int = 50, customer_ids: Iterable[int] | None = None
) -> List[Dict[str, Any]]:
    now = datetime.now(UTC)
    ids: Sequence[int] = list(customer_ids) if customer_ids is not None else list(
        range(1, count + 1)
    )
    tickets: List[Dict[str, Any]] = []
    for i in range(1, count + 1):
        created_at = now - timedelta(days=randint(0, 30))
        tickets.append(
            {
                "ticket_id": i,
                "customer_id": choice(ids),
                "subject": f"Issue {i}",
                "priority": choice(["low", "medium", "high"]),
                "created_at": created_at.isoformat(),
                "status": choice(["open", "closed"]),
            }
        )
    return tickets


def generate_analytics_days(
    count: int = 30, metric: str = "daily_active_users"
) -> List[Dict[str, Any]]:
    today = datetime.now(UTC).date()
    points: List[Dict[str, Any]] = []
    for i in range(count):
        day = today - timedelta(days=i)
        points.append(
            {
                "metric": metric,
                "date": day.isoformat(),
                "value": randint(100, 1_000),
            }
        )
    return points


def write_mock_files(base_path: str | Path = "data") -> None:
    base = Path(base_path)
    base.mkdir(parents=True, exist_ok=True)

    customers = generate_customers()
    tickets = generate_support_tickets(customer_ids=[c["customer_id"] for c in customers])
    analytics = generate_analytics_days()

    (base / "customers.json").write_text(json.dumps(customers, indent=2))
    (base / "support_tickets.json").write_text(json.dumps(tickets, indent=2))
    (base / "analytics.json").write_text(json.dumps(analytics, indent=2))

