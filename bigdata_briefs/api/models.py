from datetime import datetime, timedelta

from pydantic import BaseModel, Field


class BriefCreationRequest(BaseModel):
    watchlist_id: str = Field(
        ..., description="The ID of the watchlist for which the brief is being created."
    )
    report_start_date: datetime = Field(
        default_factory=lambda: datetime.now().replace(
            minute=0, second=0, microsecond=0
        )
        - timedelta(days=7),
        description="The start date for the report period.",
    )
    report_end_date: datetime = Field(
        default_factory=lambda: datetime.now().replace(
            minute=0, second=0, microsecond=0
        ),
        description="The end date for the report period.",
    )
    novelty: bool = Field(
        default=True,
        description="Whether to only include novel information in the report.",
    )
