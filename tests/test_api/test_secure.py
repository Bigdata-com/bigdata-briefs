import asyncio

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from bigdata_briefs.api import secure
from bigdata_briefs.api.app import app


# Fixtures for dummy settings
@pytest.fixture
def settings_no_token():
    class Settings:
        ACCESS_TOKEN = None

    return Settings


@pytest.fixture
def settings_with_token():
    class Settings:
        ACCESS_TOKEN = "secret-token"

    return Settings


@pytest.mark.parametrize("token", [None, "any", ""])
def test_no_access_token(monkeypatch, settings_no_token, token):
    """Should allow any token or no token if ACCESS_TOKEN is not set."""
    monkeypatch.setattr(secure, "settings", settings_no_token)
    assert secure.validate_access_token(token) is None


@pytest.mark.parametrize(
    "token,expected",
    [
        ("secret-token", "secret-token"),
    ],
)
def test_valid_token(monkeypatch, settings_with_token, token, expected):
    """Should accept the correct access token."""
    monkeypatch.setattr(secure, "settings", settings_with_token)
    assert secure.validate_access_token(token) == expected


@pytest.mark.parametrize("token", [None, "", "wrong-token", "another"])
def test_invalid_or_missing_token(monkeypatch, settings_with_token, token):
    """Should raise HTTPException for missing or invalid tokens when required."""
    monkeypatch.setattr(secure, "settings", settings_with_token)
    with pytest.raises(HTTPException) as exc:
        secure.validate_access_token(token)
    assert exc.value.status_code == 403
    assert exc.value.detail == "Invalid access token"


def test_require_bigdata_api_key_missing():
    with pytest.raises(HTTPException) as exc:
        asyncio.run(secure.require_bigdata_api_key(None))
    assert exc.value.status_code == 401
    assert exc.value.detail["error"] == "API key required"


def test_require_bigdata_api_key_blank():
    with pytest.raises(HTTPException) as exc:
        asyncio.run(secure.require_bigdata_api_key("   "))
    assert exc.value.status_code == 401


def test_require_bigdata_api_key_valid():
    assert asyncio.run(secure.require_bigdata_api_key("  my-key  ")) == "my-key"


def test_create_brief_requires_bigdata_api_key():
    with TestClient(app) as client:
        response = client.post(
            "/briefs/create",
            json={
                "entities": "db8478c9-34db-4975-8e44-b1ff764098ac",
                "report_start_date": "2025-10-01",
                "report_end_date": "2025-10-07",
            },
        )
        assert response.status_code == 401
