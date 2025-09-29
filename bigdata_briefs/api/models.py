from datetime import datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel, Field

from bigdata_briefs.models import BriefReport
from bigdata_briefs.settings import settings


class WorkflowStatus(StrEnum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class BriefCreationRequest(BaseModel):
    companies: list[str] | str = Field(
        "db8478c9-34db-4975-8e44-b1ff764098ac",
        description="List of RavenPack entity IDs  or a watchlist ID representing the companies to track in the generated brief.",
        examples=["db8478c9-34db-4975-8e44-b1ff764098ac"],
    )
    report_start_date: datetime = Field(
        datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(days=7),
        description="The start date for the report period.",
    )
    report_end_date: datetime = Field(
        datetime.now().replace(minute=0, second=0, microsecond=0),
        description="The end date for the report period.",
    )
    novelty: bool = Field(
        True,
        description="Whether to only include novel information in the report.",
    )
    sources: list[str] | None = Field(
        None,
        description="List of RavenPack entity IDs to filter the sources by.",
        example=["9D69F1", "B5235B"],
    )
    topics: list[str] | None = Field(
        None,
        description="A list of topics to focus on in the report. A set of handpicked topics focussing on financial relevance will be used if not provided.",
        examples=[settings.TOPICS],
    )


class BriefAcceptedResponse(BaseModel):
    request_id: str
    status: WorkflowStatus


class BriefStatusResponse(BaseModel):
    request_id: str
    last_updated: datetime
    status: WorkflowStatus
    logs: list[str] = Field(default_factory=list)
    report: BriefReport | None = None
