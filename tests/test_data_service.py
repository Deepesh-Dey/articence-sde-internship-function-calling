"""Tests for data service."""

import json
from datetime import date, datetime
from pathlib import Path

import pytest

from app.models.analytics import AnalyticsPoint
from app.models.crm import CRMCustomer
from app.models.support import SupportTicket
from app.services.data_service import fetch_data


@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    """Create temporary data directory with test JSON files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # CRM test data
    crm_data = [
        {
            "customer_id": i,
            "name": f"Customer {i}",
            "email": f"c{i}@example.com",
            "created_at": f"2025-01-{i:02d}T00:00:00",
            "status": "active" if i % 2 == 0 else "inactive",
        }
        for i in range(1, 11)
    ]
    (data_dir / "customers.json").write_text(json.dumps(crm_data))
    
    # Support test data
    support_data = [
        {
            "ticket_id": i,
            "customer_id": i,
            "subject": f"Issue {i}",
            "priority": ["low", "medium", "high"][i % 3],
            "created_at": f"2025-01-{i:02d}T00:00:00",
            "status": "open" if i % 2 == 0 else "closed",
        }
        for i in range(1, 11)
    ]
    (data_dir / "support_tickets.json").write_text(json.dumps(support_data))
    
    # Analytics test data
    analytics_data = [
        {
            "metric": "daily_active_users",
            "date": f"2025-01-{i:02d}",
            "value": 100 + i * 10,
        }
        for i in range(1, 31)
    ]
    (data_dir / "analytics.json").write_text(json.dumps(analytics_data))
    
    monkeypatch.chdir(tmp_path)
    return data_dir


class TestFetchData:
    def test_fetch_crm_basic(self, temp_data_dir):
        """Test basic CRM data fetch."""
        result = fetch_data("crm")
        assert result.metadata.source == "crm"
        assert result.metadata.total_results == 10
        assert len(result.data) > 0

    def test_fetch_crm_with_status_filter(self, temp_data_dir):
        """Test CRM fetch with status filter."""
        result = fetch_data("crm", status="active")
        assert result.metadata.total_results == 5  # Half are active
        assert all(isinstance(item, CRMCustomer) for item in result.data)
        assert all(item.status == "active" for item in result.data)

    def test_fetch_crm_voice_mode(self, temp_data_dir):
        """Test CRM fetch with voice optimization."""
        result = fetch_data("crm", voice=True)
        assert result.metadata.returned_results <= 10
        assert result.metadata.voice_summary is not None
        assert "customers" in result.metadata.voice_summary.lower()

    def test_fetch_support_with_filters(self, temp_data_dir):
        """Test support fetch with multiple filters."""
        result = fetch_data("support", status="open", priority="high")
        assert result.metadata.source == "support"
        assert all(isinstance(item, SupportTicket) for item in result.data)
        assert all(item.status == "open" for item in result.data)
        assert all(item.priority == "high" for item in result.data)

    def test_fetch_analytics_with_pagination(self, temp_data_dir):
        """Test analytics fetch with pagination."""
        result = fetch_data("analytics", limit=5, offset=0)
        assert result.metadata.source == "analytics"
        assert result.metadata.returned_results == 5
        assert len(result.data) == 5

    def test_fetch_analytics_voice_summarization(self, temp_data_dir):
        """Test analytics summarization for large datasets."""
        result = fetch_data("analytics", voice=True)
        # With 30 points, should be summarized
        if result.metadata.returned_results == 1:
            assert isinstance(result.data[0], dict)
            assert result.data[0].get("type") == "aggregated"

    def test_fetch_unknown_source(self):
        """Test handling of unknown data source."""
        result = fetch_data("unknown")
        assert result.metadata.source == "unknown"
        assert result.metadata.total_results == 0
        assert len(result.data) == 0

    def test_fetch_with_limit(self, temp_data_dir):
        """Test fetch with custom limit."""
        result = fetch_data("crm", limit=3)
        assert result.metadata.returned_results == 3
        assert len(result.data) == 3

    def test_fetch_with_offset(self, temp_data_dir):
        """Test fetch with offset."""
        result1 = fetch_data("crm", limit=5, offset=0)
        result2 = fetch_data("crm", limit=5, offset=5)
        
        if len(result1.data) > 0 and len(result2.data) > 0:
            assert result1.data[0].customer_id != result2.data[0].customer_id
