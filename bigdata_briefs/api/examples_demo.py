"""Precomputed demo briefs for Commodities and Countries watchlists."""

from __future__ import annotations

from typing import Final
from uuid import UUID

from bigdata_briefs.api.example_loader import build_example_models
from bigdata_briefs.api.sql_models import SQLWorkflowStatus
from bigdata_briefs.sql_models import SQLBriefReport

COMMODITIES_EXAMPLE_UUID: Final[UUID] = UUID("22222222-2222-2222-2222-222222222222")
COUNTRIES_EXAMPLE_UUID: Final[UUID] = UUID("33333333-3333-3333-3333-333333333333")

COMMODITIES_EXAMPLE_FILE: Final[str] = "example_commodities.json"
COUNTRIES_EXAMPLE_FILE: Final[str] = "example_countries.json"

COMMODITIES_EXAMPLE_STATUS: Final[SQLWorkflowStatus]
COMMODITIES_EXAMPLE_REPORT: Final[SQLBriefReport]
COMMODITIES_EXAMPLE_STATUS, COMMODITIES_EXAMPLE_REPORT = build_example_models(
    COMMODITIES_EXAMPLE_UUID, COMMODITIES_EXAMPLE_FILE
)

COUNTRIES_EXAMPLE_STATUS: Final[SQLWorkflowStatus]
COUNTRIES_EXAMPLE_REPORT: Final[SQLBriefReport]
COUNTRIES_EXAMPLE_STATUS, COUNTRIES_EXAMPLE_REPORT = build_example_models(
    COUNTRIES_EXAMPLE_UUID, COUNTRIES_EXAMPLE_FILE
)


def all_demo_example_models() -> list[tuple[SQLWorkflowStatus, SQLBriefReport]]:
    return [
        (COMMODITIES_EXAMPLE_STATUS, COMMODITIES_EXAMPLE_REPORT),
        (COUNTRIES_EXAMPLE_STATUS, COUNTRIES_EXAMPLE_REPORT),
    ]
