from datetime import date, datetime, timedelta
from enum import Enum, StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from bigdata_briefs.models import BriefReport
from bigdata_briefs.settings import settings


class WorkflowStatus(StrEnum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class WatchlistExample(BaseModel):
    id: str = Field(..., description="The unique identifier for the watchlist.")
    name: str = Field(..., description="The name of the watchlist.")


class ExampleWatchlists(Enum):
    MAG_7 = WatchlistExample(
        id="814d0944-a2c1-44f6-8b42-a70c0795428e", name="Magnificent 7"
    )
    MILITARIZATION = WatchlistExample(
        id="beda15f2-b3ba-44dd-80c6-79d8a1bba764", name="Defense Stocks"
    )
    HEALTH_AND_WELLNESS = WatchlistExample(
        id="eea133f7-ddc6-44bd-bd66-72f1e31dd7db", name="Health and Wellness Stocks"
    )
    HIGH_FINANCE = WatchlistExample(
        id="f7801965-ed54-4ff1-b524-b4ecee3bc858", name="High Finance Stocks"
    )
    FIN_INNOV = WatchlistExample(
        id="74cff065-9b00-4f6c-8690-5dff8cbbf3e8", name="FinTech Innovators"
    )
    AI_SZN = WatchlistExample(
        id="db8478c9-34db-4975-8e44-b1ff764098ac", name="AI Scene Stocks"
    )

    def __iter__(self):
        """Allows to create a dict from the enum
        >>> dict(ExampleWatchlists)
        {'POINT_72': {'id': '9ab396cf-a2bb-4c91-b9bf-ed737905803e', 'name': 'Point 72 Holdings'}, ...}
        """
        yield self.name
        yield self.value.model_dump()


class BriefCreationRequest(BaseModel):
    companies: list[str] | str = Field(
        ...,
        description="List of RavenPack entity IDs  or a watchlist ID representing the companies to track in the generated brief.",
        examples=[ExampleWatchlists.AI_SZN.value.id],
    )
    report_start_date: datetime = Field(
        ...,
        description="The start date for the report period.",
        examples=[date.today() - timedelta(days=7)],
    )
    report_end_date: datetime = Field(
        ...,
        description="The end date for the report period.",
        examples=[date.today()],
    )
    novelty: bool = Field(
        True,
        description="Whether to only include novel information in the report.",
        examples=[True],
    )
    sources: list[str] | None = Field(
        None,
        description="List of RavenPack entity IDs to filter the sources by.",
        examples=[None],
    )
    topics: list[str] | None = Field(
        None,
        description="A list of topics to focus on in the report. A set of handpicked topics focussing on financial relevance will be used if not provided.",
        examples=[settings.TOPICS],
    )
    source_rank_boost: int | None = Field(
        None,
        description="Controls how much the source rank influences relevance. 0 -> source rank has no effect. 10 -> maximum effect, boosting chunks from premium sources.",
        ge=0,
        le=10,
        examples=[settings.API_SOURCE_RANK_BOOST],
    )
    freshness_boost: int | None = Field(
        None,
        description="Controls the influence of document timestamp on relevance. 0 -> publishing time is ignored (useful for point-in-time research). 10 -> most recent documents are heavily prioritized.",
        ge=0,
        le=10,
        examples=[settings.API_FRESHNESS_BOOST],
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


class WorkflowRunInfo(BaseModel):
    id: UUID
    status: str
    last_updated: datetime
    log_count: int


class ReportInfo(BaseModel):
    id: UUID
    watchlist_id: str
    created_at: datetime
    report_period_start: datetime
    report_period_end: datetime
    novelty_enabled: bool
    is_empty: bool


class BulletPointInfo(BaseModel):
    id: UUID
    entity_id: str
    date: datetime
    original_text: str


class DatabaseStatusResponse(BaseModel):
    workflow_runs: list[WorkflowRunInfo] = Field(default_factory=list)
    reports: list[ReportInfo] = Field(default_factory=list)
    bullet_points: list[BulletPointInfo] = Field(default_factory=list)
    total_workflow_runs: int = 0
    total_reports: int = 0
    total_bullet_points: int = 0


class DiscardedBulletPointDebug(BaseModel):
    text: str
    max_similarity: float
    most_similar_text: str


class EntityDebugInfo(BaseModel):
    entity_id: str
    entity_name: str
    generated_texts: list[str]
    compared_with: list[str]
    discarded: list[DiscardedBulletPointDebug]
    kept_texts: list[str]


class DebugDataResponse(BaseModel):
    request_id: str
    entities: dict[str, EntityDebugInfo] = Field(default_factory=dict)
