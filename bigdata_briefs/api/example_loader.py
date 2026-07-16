"""Helpers to build demo brief models from precomputed JSON brief reports."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from bigdata_briefs.api.sql_models import SQLWorkflowStatus
from bigdata_briefs.sql_models import SQLBriefReport


def load_brief_report(filename: str) -> dict:
    """Load a precomputed brief report JSON located next to this module."""
    path = Path(__file__).with_name(filename)
    return json.loads(path.read_text(encoding="utf-8"))


def _build_status(example_uuid: UUID, brief_report: dict) -> SQLWorkflowStatus:
    entity_reports = brief_report.get("entity_reports", [])
    total = len(entity_reports)
    with_info = sum(1 for entity in entity_reports if entity.get("content"))
    without_info = total - with_info
    return SQLWorkflowStatus(
        id=example_uuid,
        last_updated=datetime.now(),
        status="completed",
        logs=[
            "Validating input parameters",
            "Generating report per entity",
            (
                f"Generated reports for {total} entities, {with_info} with "
                f"information, {without_info} without information and 0 failed."
            ),
            "Generating introduction section",
            "Introduction section generated",
            "Storing output report",
        ],
    )


def _build_report(example_uuid: UUID, brief_report: dict) -> SQLBriefReport:
    return SQLBriefReport(
        id=example_uuid,
        watchlist_id=brief_report["watchlist_id"],
        created_at=datetime.now(),
        is_empty=brief_report.get("is_empty", False),
        report_period_start=datetime.fromisoformat(brief_report["start_date"]),
        report_period_end=datetime.fromisoformat(brief_report["end_date"]),
        novelty_enabled=brief_report.get("novelty", True),
        brief_report=brief_report,
    )


def build_example_models(
    example_uuid: UUID, filename: str
) -> tuple[SQLWorkflowStatus, SQLBriefReport]:
    """Build the (status, report) pair for a demo brief loaded from JSON."""
    brief_report = load_brief_report(filename)
    return (
        _build_status(example_uuid, brief_report),
        _build_report(example_uuid, brief_report),
    )
