import uuid
from datetime import datetime

from sqlmodel import JSON, Column, Field, SQLModel


class SQLBriefReport(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    watchlist_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_empty: bool = Field(default=False)
    report_period_start: datetime
    report_period_end: datetime
    novelty_enabled: bool = Field(default=True)
    brief_report: dict = Field(sa_column=Column(JSON))


class SQLReportsSources(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    brief_id: uuid.UUID = Field(index=True, foreign_key="sqlbriefreport.id")
    report_sources: dict = Field(sa_column=Column(JSON))
