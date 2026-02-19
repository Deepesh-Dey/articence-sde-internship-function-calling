"""Tests for data connectors."""

import json
import tempfile
from datetime import date, datetime
from pathlib import Path

import pytest

from app.connectors.analytics_connector import AnalyticsConnector
from app.connectors.crm_connector import CRMConnector
from app.connectors.support_connector import SupportConnector
from app.models.analytics import AnalyticsPoint
from app.models.crm import CRMCustomer
from app.models.support import SupportTicket


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory with test JSON files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # CRM test data
    crm_data = [
        {
            "customer_id": 1,
            "name": "Test Customer",
            "email": "test@example.com",
            "created_at": "2025-01-01T00:00:00",
            "status": "active",
        }
    ]
    (data_dir / "customers.json").write_text(json.dumps(crm_data))
    
    # Support test data
    support_data = [
        {
            "ticket_id": 1,
            "customer_id": 1,
            "subject": "Test Issue",
            "priority": "high",
            "created_at": "2025-01-01T00:00:00",
            "status": "open",
        }
    ]
    (data_dir / "support_tickets.json").write_text(json.dumps(support_data))
    
    # Analytics test data
    analytics_data = [
        {
            "metric": "daily_active_users",
            "date": "2025-01-01",
            "value": 100,
        }
    ]
    (data_dir / "analytics.json").write_text(json.dumps(analytics_data))
    
    return data_dir


class TestCRMConnector:
    def test_fetch_success(self, temp_data_dir, monkeypatch):
        """Test successful CRM data fetch."""
        monkeypatch.chdir(temp_data_dir.parent)
        connector = CRMConnector()
        result = connector.fetch()
        
        assert len(result) == 1
        assert isinstance(result[0], CRMCustomer)
        assert result[0].customer_id == 1
        assert result[0].name == "Test Customer"
        assert result[0].status == "active"

    def test_fetch_file_not_found(self, monkeypatch):
        """Test handling of missing file."""
        monkeypatch.chdir(Path("/tmp"))
        connector = CRMConnector()
        
        with pytest.raises(FileNotFoundError):
            connector.fetch()

    def test_fetch_invalid_json(self, tmp_path, monkeypatch):
        """Test handling of invalid JSON."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "customers.json").write_text("invalid json")
        monkeypatch.chdir(tmp_path)
        
        connector = CRMConnector()
        with pytest.raises(json.JSONDecodeError):
            connector.fetch()


class TestSupportConnector:
    def test_fetch_success(self, temp_data_dir, monkeypatch):
        """Test successful support tickets fetch."""
        monkeypatch.chdir(temp_data_dir.parent)
        connector = SupportConnector()
        result = connector.fetch()
        
        assert len(result) == 1
        assert isinstance(result[0], SupportTicket)
        assert result[0].ticket_id == 1
        assert result[0].priority == "high"
        assert result[0].status == "open"


class TestAnalyticsConnector:
    def test_fetch_success(self, temp_data_dir, monkeypatch):
        """Test successful analytics fetch."""
        monkeypatch.chdir(temp_data_dir.parent)
        connector = AnalyticsConnector()
        result = connector.fetch()
        
        assert len(result) == 1
        assert isinstance(result[0], AnalyticsPoint)
        assert result[0].metric == "daily_active_users"
        assert result[0].value == 100
        assert result[0].date == date(2025, 1, 1)
