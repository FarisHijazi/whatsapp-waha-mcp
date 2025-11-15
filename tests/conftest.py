"""Pytest configuration and fixtures."""

import os
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest


@pytest.fixture
def mock_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("WAHA_BASE_URL", "http://localhost:3000")
    monkeypatch.setenv("WAHA_API_KEY", "test-api-key")


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx response."""
    def _create_response(status_code=200, json_data=None):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_data or {"success": True}
        response.text = str(json_data or {})
        response.raise_for_status = MagicMock()
        if status_code >= 400:
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error", request=MagicMock(), response=response
            )
        return response
    return _create_response


@pytest.fixture
def mock_http_client(mock_httpx_response):
    """Create a mock HTTP client."""
    client = AsyncMock()
    client.request = AsyncMock(return_value=mock_httpx_response())
    return client


@pytest.fixture(autouse=True)
def reset_http_client():
    """Reset global HTTP client between tests."""
    import whatsapp_waha_mcp.server as server
    server.http_client = None
    yield
    server.http_client = None
