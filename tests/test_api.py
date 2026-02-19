"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestDataEndpoint:
    def test_get_crm_data(self):
        """Test fetching CRM data."""
        response = client.get("/data/crm?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert data["metadata"]["source"] == "crm"

    def test_get_support_data_with_filters(self):
        """Test fetching support data with filters."""
        response = client.get("/data/support?status=open&priority=high&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["source"] == "support"

    def test_get_analytics_data(self):
        """Test fetching analytics data."""
        response = client.get("/data/analytics?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["source"] == "analytics"

    def test_unknown_source(self):
        """Test handling of unknown data source."""
        response = client.get("/data/unknown")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["total_results"] == 0
        assert data["metadata"]["source"] == "unknown"

    def test_voice_mode(self):
        """Test voice optimization mode."""
        response = client.get("/data/crm?voice=true")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["returned_results"] <= 10
        assert data["metadata"].get("voice_summary") is not None

    def test_pagination(self):
        """Test pagination parameters."""
        response1 = client.get("/data/crm?limit=5&offset=0")
        response2 = client.get("/data/crm?limit=5&offset=5")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Should return different items
        if len(data1["data"]) > 0 and len(data2["data"]) > 0:
            assert data1["data"][0] != data2["data"][0]


class TestLLMEndpoints:
    def test_get_tools_openai(self):
        """Test getting OpenAI tool definitions."""
        response = client.get("/llm/tools?provider=openai")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 3
        assert data["tools"][0]["type"] == "function"

    def test_get_tools_anthropic(self):
        """Test getting Anthropic tool definitions."""
        response = client.get("/llm/tools?provider=anthropic")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 3
        assert "name" in data["tools"][0]

    def test_get_tools_invalid_provider(self):
        """Test handling of invalid provider."""
        response = client.get("/llm/tools?provider=invalid")
        assert response.status_code == 400

    def test_execute_tool_call(self):
        """Test executing a tool call."""
        response = client.post(
            "/llm/query",
            json={"tool": "get_crm_data", "arguments": {"status": "active", "voice": True}},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert data["metadata"]["source"] == "crm"

    def test_execute_tool_call_unknown_tool(self):
        """Test handling of unknown tool."""
        response = client.post(
            "/llm/query",
            json={"tool": "unknown_tool", "arguments": {}},
        )
        assert response.status_code == 400
