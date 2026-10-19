import uuid
from datetime import datetime

from pydantic import NaiveDatetime
from sqlmodel import JSON, Column, Field, SQLModel


class SQLBriefReport(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    watchlist_id: str
    created_at: NaiveDatetime = Field(default_factory=datetime.now)
    is_empty: bool = Field(default=False)
    report_period_start: NaiveDatetime
    report_period_end: NaiveDatetime
    novelty_enabled: bool = Field(default=True)
    brief_report: dict = Field(sa_column=Column(JSON))
