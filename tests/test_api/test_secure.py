import pytest
from fastapi import HTTPException

from bigdata_briefs.api import secure


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
