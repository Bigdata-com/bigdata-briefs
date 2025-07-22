import itertools
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Semaphore
from typing import Callable, Protocol

import bigdata_client.query as Q
from bigdata_client import Bigdata
from bigdata_client.daterange import AbsoluteDateRange
from bigdata_client.models.search import DocumentType, SortBy
from bigdata_client.models.watchlists import Watchlist
from pydantic import BaseModel, ValidationError

from bigdata_briefs import logger
from bigdata_briefs.exceptions import TooManySDKRetriesError
from bigdata_briefs.metrics import ContentMetrics
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
    source_list_exploration: list[str] | None = None
    rerank_threshold: float
    max_source_rank_allowed: int | None = None


class CheckIfThereAreResultsSearchConfig(BaseModel):
    source_list_exploration: list[str] | None = None
    sentiment_threshold: float | None = None
    document_limit: int = 1
    use_topics: bool = False
    rerank_threshold: float = 0.0
    max_source_rank_allowed: int | None = None


class ExploratorySearchConfig(BaseModel):
    source_list_exploration: list[str] | None = None
    sentiment_threshold: float | None = settings.EXPLORATORY_SENTIMENT_THRESHOLD
    document_limit: int = settings.SDK_DOCS_LIMIT_EXPLORATORY
    use_topics: bool = True
    rerank_threshold: float = settings.SDK_RERANK_EXPLORATORY
    max_source_rank_allowed: int | None = None


class FollowUpQuestionsSearchConfig(BaseModel):
    source_list_exploration: list[str] | None = None
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
        return self.client.watchlists.get(watchlist_id)

    def get_entities(self, entity_ids: list[str]) -> list[Entity]:
        results = self.client.knowledge_graph.get_entities(entity_ids)
        entities = []
        for obj in results:
            entities.append(Entity.from_sdk(obj))
        return entities

    @log_args
    @log_return_value
    @log_time
    def sdk_search(
        self, *args, limit, max_source_rank_allowed: int | None = None, **kwargs
    ):
        search = self._call_sdk_method(self.client.search.new, *args, **kwargs)
        results = self._call_sdk_method(search.run, limit)

        parsed_results = []
        for result in results:
            if (
                max_source_rank_allowed is not None
                and result.source.rank <= max_source_rank_allowed
            ):
                continue
            parsed_results.append(Result.from_sdk(result))

        return parsed_results

    def _call_sdk_method(self, method: Callable, *args, **kwargs):
        e = None
        with self.semaphore:
            for attempt in range(settings.SDK_RETRIES):
                try:
                    return method(*args, **kwargs)
                except Exception as e:
                    logger.warning(
                        f"Error calling SDK method {method.__name__}: {e}. Attempt {attempt + 1}"
                    )
                    sleep_with_backoff(attempt=attempt)

        raise TooManySDKRetriesError(
            f"Too many SDK retries {method.__name__}. Last error {e}"
        )

    @log_performance
    def check_if_entity_has_results(
        self,
        entity_id: str,
        report_dates: ReportDates,
        config: CheckIfThereAreResultsSearchConfig = CheckIfThereAreResultsSearchConfig(),
        max_source_rank_allowed: int | None = None,
        similarity_text: str | None = None,
    ) -> list[Result]:
        """
        Make a simple query to find if the entity has results.
        Based on this, the next steps will happen or not.
        """

        query = build_query(
            entity_id=entity_id,
            config=config,
            report_dates=report_dates,
            similarity_text=similarity_text,
        )
        results = self.sdk_search(
            query,
            limit=config.document_limit,
            scope=DocumentType.ALL,
            sortby=SortBy.RELEVANCE,
            rerank_threshold=config.rerank_threshold,
            max_source_rank_allowed=config.max_source_rank_allowed,
        )

        ContentMetrics.track_usage(
            TopicContentTracker(
                topic="Check if entity has results",
                retrieval=TopicContentTracker.retrieval_from_sdk_result(
                    sdk_results=results,
                    entity_id=entity_id,
                ),
            )
        )

        return results

    @log_performance
    def _run_single_exploratory_search(
        self,
        entity_id: str,
        report_dates: ReportDates,
        config: ExploratorySearchConfig,
        max_source_rank_allowed: int | None = None,
        similarity_text: str | None = None,
        topic: str | None = None,
    ):
        query = build_query(
            entity_id=entity_id,
            config=config,
            report_dates=report_dates,
            similarity_text=similarity_text,
        )

        results = self.sdk_search(
            query,
            limit=config.document_limit,
            scope=DocumentType.ALL,
            sortby=SortBy.RELEVANCE,
            rerank_threshold=config.rerank_threshold,
            max_source_rank_allowed=config.max_source_rank_allowed,
        )

        if topic:
            ContentMetrics.track_usage(
                TopicContentTracker(
                    topic=topic,
                    retrieval=TopicContentTracker.retrieval_from_sdk_result(
                        sdk_results=results,
                        entity_id=entity_id,
                    ),
                )
            )

        return results

    @log_performance
    @log_args
    @log_return_value
    def run_exploratory_search(
        self,
        entity: Entity,
        report_dates: ReportDates,
        executor: ThreadPoolExecutor,
        config: ExploratorySearchConfig = ExploratorySearchConfig(),
    ) -> list[Result]:
        if config.use_topics:
            # TODO use jinja2
            company_topics = [
                t.format(company=entity.name) for t in settings.TOPICS.values()
            ]
            futures = [
                executor.submit(
                    self._run_single_exploratory_search,
                    entity_id=entity.id,
                    similarity_text=similarity_text,
                    topic=topic,
                    report_dates=report_dates,
                    config=config,
                    enable_metric=True,  # noqa
                    metric_name=f"Exploratory search. Entity {entity.id}",  # noqa
                )
                for similarity_text, topic in zip(
                    company_topics, settings.TOPICS.values()
                )
            ]
            # In addition to searching by topics, query with just the entity
            futures.append(
                executor.submit(
                    self._run_single_exploratory_search,
                    entity_id=entity.id,
                    report_dates=report_dates,
                    config=config,
                    enable_metric=True,  # noqa
                    metric_name=f"Exploratory search. Entity {entity.id}",  # noqa
                )
            )
            # Remove duplicates and return as a list
            v = list(set(itertools.chain(*(f.result() for f in as_completed(futures)))))

            return v

        else:
            return self._run_single_exploratory_search(
                entity_id=entity.id,
                report_dates=report_dates,
                config=config,
                enable_metric=True,
                metric_name=f"Exploratory search. Entity {entity.id}",
            )

    def _run_follow_up_single_question(
        self,
        entity_id: str,
        question: str | None,
        report_dates: ReportDates,
        max_source_rank_allowed: int | None = None,
        config: FollowUpQuestionsSearchConfig = FollowUpQuestionsSearchConfig(),
    ):
        query = build_query(
            entity_id=entity_id,
            config=config,
            report_dates=report_dates,
            similarity_text=question,
        )

        results = self.sdk_search(
            query,
            limit=config.document_limit,
            rerank_threshold=config.rerank_threshold,
            scope=DocumentType.ALL,
            sortby=SortBy.RELEVANCE,
        )

        ContentMetrics.track_usage(
            TopicContentTracker(
                topic="Follow up questions",
                retrieval=TopicContentTracker.retrieval_from_sdk_result(
                    sdk_results=results,
                    entity_id=entity_id,
                ),
            )
        )

        return results

    @log_performance
    def run_query_with_follow_up_questions(
        self,
        entity: Entity,
        follow_up_questions: list[str],
        report_dates: ReportDates,
        executor: ThreadPoolExecutor,
    ) -> QAPairs:
        future_to_question = {
            executor.submit(
                self._run_follow_up_single_question,
                entity_id=entity.id,
                question=question,
                report_dates=report_dates,
            ): question
            for question in follow_up_questions
        }
        qa_pairs = []
        for future in as_completed(future_to_question):
            try:
                qa_pairs.append(
                    QuestionAnswer(
                        question=future_to_question[future],
                        answer=future.result(),
                    )
                )
            except ValidationError as e:
                logger.warning(
                    f"Error running follow up questions for entity {entity}: {e}"
                )

        return QAPairs(pairs=qa_pairs)


@log_args
def build_query(
    entity_id: str,
    config: SearchConfig,
    report_dates: ReportDates,
    similarity_text: str | None,
):
    # Always constrain by date range
    search_criteria = AbsoluteDateRange(start=report_dates.start, end=report_dates.end)

    if similarity_text:
        search_criteria &= Q.Similarity(similarity_text)

    # Check if entity_id is presumably a known entity or a topic
    if len(entity_id) == 6:
        search_criteria &= Q.Entity(entity_id)
    else:
        search_criteria &= Q.Topic(entity_id)

    # If a sentiment threshold is provided, filter for strong positive/negative
    if config.sentiment_threshold:
        search_criteria &= Q.SentimentRange(
            (config.sentiment_threshold, 1)
        ) | Q.SentimentRange((-1, -config.sentiment_threshold))

    # Use high-quality sources if desired
    if config.source_list_exploration is not None:
        search_criteria &= Q.Source(*config.source_list_exploration)

    return search_criteria
