from datetime import datetime, timedelta

from pydantic import BaseModel, Field


class BriefCreationRequest(BaseModel):
    watchlist_id: str = Field(
        "db8478c9-34db-4975-8e44-b1ff764098ac",
        description="The ID of the watchlist for which the brief is being created.",
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
