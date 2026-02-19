"""Tests for business rules engine."""

from datetime import date, datetime

import pytest

from app.models.analytics import AnalyticsPoint
from app.models.crm import CRMCustomer
from app.models.support import SupportTicket
from app.services.business_rules import (
    apply_filters,
    apply_pagination,
    apply_voice_limits,
    prioritize_recent,
)


@pytest.fixture
def sample_customers():
    """Sample CRM customers for testing."""
    return [
        CRMCustomer(
            customer_id=1,
            name="Customer 1",
            email="c1@example.com",
            created_at=datetime(2025, 1, 1),
            status="active",
        ),
        CRMCustomer(
            customer_id=2,
            name="Customer 2",
            email="c2@example.com",
            created_at=datetime(2025, 1, 2),
            status="inactive",
        ),
        CRMCustomer(
            customer_id=3,
            name="Customer 3",
            email="c3@example.com",
            created_at=datetime(2025, 1, 3),
            status="active",
        ),
    ]


@pytest.fixture
def sample_tickets():
    """Sample support tickets for testing."""
    return [
        SupportTicket(
            ticket_id=1,
            customer_id=1,
            subject="Issue 1",
            priority="high",
            created_at=datetime(2025, 1, 1),
            status="open",
        ),
        SupportTicket(
            ticket_id=2,
            customer_id=2,
            subject="Issue 2",
            priority="low",
            created_at=datetime(2025, 1, 2),
            status="closed",
        ),
    ]


@pytest.fixture
def sample_analytics():
    """Sample analytics points for testing."""
    return [
        AnalyticsPoint(metric="daily_active_users", date=date(2025, 1, 1), value=100),
        AnalyticsPoint(metric="daily_active_users", date=date(2025, 1, 2), value=200),
        AnalyticsPoint(metric="revenue", date=date(2025, 1, 1), value=1000),
    ]


class TestPrioritizeRecent:
    def test_prioritize_customers(self, sample_customers):
        """Test sorting customers by created_at descending."""
        result = prioritize_recent(sample_customers)
        assert result[0].created_at == datetime(2025, 1, 3)
        assert result[-1].created_at == datetime(2025, 1, 1)

    def test_prioritize_analytics(self, sample_analytics):
        """Test sorting analytics by date descending."""
        result = prioritize_recent(sample_analytics)
        assert result[0].date == date(2025, 1, 2)
        assert result[-1].date == date(2025, 1, 1)

    def test_empty_list(self):
        """Test handling of empty list."""
        assert prioritize_recent([]) == []


class TestApplyFilters:
    def test_filter_crm_by_status(self, sample_customers):
        """Test filtering CRM customers by status."""
        result = apply_filters(sample_customers, status="active")
        assert len(result) == 2
        assert all(c.status == "active" for c in result)

    def test_filter_support_by_status_and_priority(self, sample_tickets):
        """Test filtering support tickets by status and priority."""
        result = apply_filters(sample_tickets, status="open", priority="high")
        assert len(result) == 1
        assert result[0].status == "open"
        assert result[0].priority == "high"

    def test_filter_analytics_by_metric(self, sample_analytics):
        """Test filtering analytics by metric name."""
        result = apply_filters(sample_analytics, metric="daily_active_users")
        assert len(result) == 2
        assert all(a.metric == "daily_active_users" for a in result)

    def test_no_filters(self, sample_customers):
        """Test that no filters returns all data."""
        result = apply_filters(sample_customers)
        assert len(result) == len(sample_customers)


class TestApplyVoiceLimits:
    def test_limit_to_max_results(self, sample_customers):
        """Test limiting results to MAX_RESULTS."""
        result = apply_voice_limits(sample_customers, limit=2)
        assert len(result) == 2

    def test_no_limit_needed(self, sample_customers):
        """Test when data is already within limit."""
        result = apply_voice_limits(sample_customers[:2], limit=10)
        assert len(result) == 2


class TestApplyPagination:
    def test_pagination_with_offset(self, sample_customers):
        """Test pagination with offset."""
        result = apply_pagination(sample_customers, offset=1, limit=2)
        assert len(result) == 2
        assert result[0].customer_id == 2

    def test_pagination_no_offset(self, sample_customers):
        """Test pagination without offset."""
        result = apply_pagination(sample_customers, offset=0, limit=2)
        assert len(result) == 2
        assert result[0].customer_id == 1

    def test_pagination_exceeds_data(self, sample_customers):
        """Test pagination when limit exceeds available data."""
        result = apply_pagination(sample_customers, offset=0, limit=10)
        assert len(result) == 3
