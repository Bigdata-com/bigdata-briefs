from datetime import datetime, timedelta
from enum import Enum, StrEnum

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
    POINT_72 = WatchlistExample(
        id="9ab396cf-a2bb-4c91-b9bf-ed737905803e", name="Point 72 Holdings"
    )
    MILITARIZATION = WatchlistExample(
        id="beda15f2-b3ba-44dd-80c6-79d8a1bba764", name="Militarization"
    )
    US_LARGE_CAP_100 = WatchlistExample(
        id="44118802-9104-4265-b97a-2e6d88d74893", name="US Large Cap 100"
    )
    HIGH_FINANCE = WatchlistExample(
        id="f7801965-ed54-4ff1-b524-b4ecee3bc858", name="High Finance"
    )
    THIRD_POINT_HOLDINGS = WatchlistExample(
        id="ec300f6f-64f0-4897-9f63-82e8d60a7e5a", name="Third Point Holdings"
    )
    THE_STREET_INDEX = WatchlistExample(
        id="ccfe5dc2-0c92-42d7-861c-1d8ee74a9e02", name="The Street Index"
    )
    AI_SZN = WatchlistExample(id="db8478c9-34db-4975-8e44-b1ff764098ac", name="AI Szn")

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
        example=ExampleWatchlists.AI_SZN.value.id,
    )
    report_start_date: datetime = Field(
        ...,
        description="The start date for the report period.",
        example=datetime.now().replace(minute=0, second=0, microsecond=0)
        - timedelta(days=7),
    )
    report_end_date: datetime = Field(
        ...,
        description="The end date for the report period.",
        example=datetime.now().replace(minute=0, second=0, microsecond=0),
    )
    novelty: bool = Field(
        True,
        description="Whether to only include novel information in the report.",
        example=True,
    )
    sources: list[str] | None = Field(
        None,
        description="List of RavenPack entity IDs to filter the sources by.",
        example=["9D69F1", "B5235B"],
    )
    topics: list[str] | None = Field(
        None,
        description="A list of topics to focus on in the report. A set of handpicked topics focussing on financial relevance will be used if not provided.",
        example=settings.TOPICS,
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
