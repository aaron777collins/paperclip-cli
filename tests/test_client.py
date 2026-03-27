"""Tests for PaperclipClient."""
import json
import pytest
import responses as rsps
from paperclip_cli.client import PaperclipClient, PaperclipError


@pytest.fixture
def client():
    return PaperclipClient(base_url="http://localhost:3100", token="test-token")


@rsps.activate
def test_health_ok(client):
    rsps.add(rsps.GET, "http://localhost:3100/api/health", json={"status": "ok"})
    result = client.health()
    assert result["status"] == "ok"


@rsps.activate
def test_health_error(client):
    rsps.add(rsps.GET, "http://localhost:3100/api/health", status=503)
    with pytest.raises(PaperclipError) as exc_info:
        client.health()
    assert exc_info.value.status_code == 503


@rsps.activate
def test_get_companies(client):
    rsps.add(rsps.GET, "http://localhost:3100/api/companies", json=[{"id": "1", "name": "TestCo"}])
    result = client.get("/companies")
    assert isinstance(result, list)
    assert result[0]["name"] == "TestCo"


@rsps.activate
def test_post_company(client):
    rsps.add(rsps.POST, "http://localhost:3100/api/companies", json={"id": "abc", "name": "New Co"}, status=201)
    result = client.post("/companies", {"name": "New Co"})
    assert result["id"] == "abc"


@rsps.activate
def test_auth_header(client):
    rsps.add(rsps.GET, "http://localhost:3100/api/health", json={})
    client.health()
    assert rsps.calls[0].request.headers["Authorization"] == "Bearer test-token"
