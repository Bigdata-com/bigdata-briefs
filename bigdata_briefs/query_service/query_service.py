import itertools
import warnings
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Semaphore
from types import FunctionType
from typing import Protocol

import bigdata_client.query as Q
from bigdata_client import Bigdata
from bigdata_client.daterange import AbsoluteDateRange
from bigdata_client.models.search import DocumentType, SortBy
from bigdata_client.models.watchlists import Watchlist
from pydantic import BaseModel, ValidationError

from bigdata_briefs import logger
from bigdata_briefs.exceptions import TooManySDKRetriesError
from bigdata_briefs.metrics import ContentMetrics, QueryUnitMetrics, WarningsMetrics
from bigdata_briefs.models import (
    Entity,
    QAPairs,
    QuestionAnswer,
    ReportDates,
    Result,
    TopicContentTracker,
)
from bigdata_briefs.settings import settings
from bigdata_briefs.utils import (
    log_args,
    log_performance,
    log_return_value,
    log_time,
    sleep_with_backoff,
)


class SearchConfig(Protocol):
    sentiment_threshold: float | None
    document_limit: int
    source_filter: list[str] | None = None
    rerank_threshold: float
    max_source_rank_allowed: int | None = None


class CheckIfThereAreResultsSearchConfig(BaseModel):
    source_filter: list[str] | None = None
    sentiment_threshold: float | None = None
    document_limit: int = 1
    use_topics: bool = False
    rerank_threshold: float = 0.0
    max_source_rank_allowed: int | None = None


class ExploratorySearchConfig(BaseModel):
    source_filter: list[str] | None = None
    sentiment_threshold: float | None = settings.EXPLORATORY_SENTIMENT_THRESHOLD
    document_limit: int = settings.SDK_DOCS_LIMIT_EXPLORATORY
    use_topics: bool = True
    rerank_threshold: float = settings.SDK_RERANK_EXPLORATORY
    max_source_rank_allowed: int | None = None


class FollowUpQuestionsSearchConfig(BaseModel):
    source_filter: list[str] | None = None
    sentiment_threshold: float | None = settings.FOLLOWUP_SENTIMENT_THRESHOLD
    document_limit: int = settings.SDK_DOCS_LIMIT_FOLLOWUP
    rerank_threshold: float = settings.SDK_RERANK_FOLLOWUP
    max_source_rank_allowed: int | None = None


class QueryService:
    def __init__(
        self,
    ):
        self.client = Bigdata(api_key=settings.BIGDATA_API_KEY)
        self.semaphore = Semaphore(
            value=settings.SDK_SIMULTANEOUS_REQUESTS
        )  # Max number of concurrent connections to the SDK

    def get_watchlist(self, watchlist_id: str) -> Watchlist:
        ...

    def get_entities(self, entity_ids: list[str]) -> list[Entity]:
        ...


    @log_performance
    def check_if_entity_has_results(
        self,
        entity_id: str,
        report_dates: ReportDates,
        config: CheckIfThereAreResultsSearchConfig = CheckIfThereAreResultsSearchConfig(),
        similarity_text: str | None = None,
    ) -> list[Result]:
        ...

    @log_performance
    def _run_single_exploratory_search(
        self,
        entity_id: str,
        report_dates: ReportDates,
        config: ExploratorySearchConfig,
        similarity_text: str | None = None,
        topic: str | None = None,
    ):
        ...

    @log_performance
    @log_args
    @log_return_value
    def run_exploratory_search(
        self,
        entity: Entity,
        topics: list[str],
        report_dates: ReportDates,
        executor: ThreadPoolExecutor,
        config: ExploratorySearchConfig = ExploratorySearchConfig(),
    ) -> list[Result]:
        ...

    def _run_follow_up_single_question(
        self,
        entity_id: str,
        question: str | None,
        report_dates: ReportDates,
        config: FollowUpQuestionsSearchConfig = FollowUpQuestionsSearchConfig(),
    ):
        ...

    @log_performance
    def run_query_with_follow_up_questions(
        self,
        entity: Entity,
        follow_up_questions: list[str],
        report_dates: ReportDates,
        source_filter: list[str] | None,
        executor: ThreadPoolExecutor,
    ) -> QAPairs:
        ...
