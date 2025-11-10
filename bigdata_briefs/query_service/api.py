import itertools
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Semaphore

import httpx
from bigdata_client import Bigdata
from bigdata_client.models.watchlists import Watchlist
from pydantic import ValidationError

from bigdata_briefs import logger
from bigdata_briefs.exceptions import TooManyAPIRetriesError
from bigdata_briefs.metrics import ContentMetrics, QueryUnitMetrics
from bigdata_briefs.models import (
    Entity,
    QAPairs,
    QuestionAnswer,
    ReportDates,
    Result,
    TopicContentTracker,
)
from bigdata_briefs.query_service.base import BaseQueryService
from bigdata_briefs.query_service.models import SearchAPIQueryDict
from bigdata_briefs.query_service.rate_limit import RequestsPerMinuteController
from bigdata_briefs.settings import settings
from bigdata_briefs.utils import (
    log_args,
    log_performance,
    log_return_value,
    log_time,
    sleep_with_backoff,
)

MAX_REQUESTS_PER_MINUTE = (
    460  # Backend rate limit (500 max, using 460 for maximum safety margin)
)
REFRESH_FREQUENCY_RATE_LIMIT = 5  # Time in seconds to pro-rate the rate limiter, lower values = smoother requests, more overhead
TIME_BEFORE_RETRY_RATE_LIMITER = 1.0  # Time in seconds before retrying the request

MAX_ENTITIES_PER_KG_ENTITY_BY_ID_REQUEST = (
    100  # Max number of entities per request to /v1/knowledge-graph/entities/id
)


class APIQueryService(BaseQueryService):
    def __init__(
        self,
    ):
        self._api_key = settings.BIGDATA_API_KEY
        self.semaphore = Semaphore(
            value=settings.API_SIMULTANEOUS_REQUESTS
        )  # Max number of concurrent connections to the SDK
        self._client = httpx.Client(
            base_url=settings.API_BASE_URL,
            headers=self.headers,
            timeout=settings.API_TIMEOUT_SECONDS,
        )
        self.rate_limit_controller = RequestsPerMinuteController(
            max_requests_per_min=MAX_REQUESTS_PER_MINUTE,
            rate_limit_refresh_frequency=REFRESH_FREQUENCY_RATE_LIMIT,
            seconds_before_retry=TIME_BEFORE_RETRY_RATE_LIMITER,
        )

        # Watchlists are not available in the API client yet, so we use the SDK for that
        self.sdk_client = Bigdata(api_key=settings.BIGDATA_API_KEY)

    @property
    def headers(self) -> dict[str, str]:
        return {"X-API-KEY": self._api_key, "Content-Type": "application/json"}

    def cleanup(self):
        self._client.close()

    def get_watchlist(self, watchlist_id: str) -> Watchlist:
        return self.sdk_client.watchlists.get(watchlist_id)

    def get_entities(self, entity_ids: list[str]) -> list[Entity]:
        # Batch entity_ids into chunks
        def batched(iterable, n):
            for i in range(0, len(iterable), n):
                yield iterable[i : i + n]

        entities = []
        for batch in batched(entity_ids, MAX_ENTITIES_PER_KG_ENTITY_BY_ID_REQUEST):
            raw_entities = self._call_api(
                endpoint="/v1/knowledge-graph/entities/id",
                method="POST",
                payload={"values": batch},
                headers=self.headers,
            )
            for entity_data in raw_entities["results"].values():
                entities.append(Entity.from_api(entity_data))

        return entities

    @log_args
    @log_return_value
    @log_time
    def api_search(self, endpoint: str, method: str, payload: dict):
        results = self._call_api(endpoint, method, payload, self.headers)

        QueryUnitMetrics.track_usage(results["usage"]["api_query_units"])

        parsed_results = []
        for result in results["results"]:
            parsed_results.append(Result.from_api(result))

        return parsed_results

    def _call_api(
        self, endpoint: str, method: str, payload: dict, headers: dict
    ) -> dict:
        with self.semaphore:
            for attempt in range(settings.API_RETRIES):
                try:
                    result = self.rate_limit_controller(
                        self._client.request,
                        method=method,
                        url=endpoint,
                        json=payload,
                        headers=headers,
                    )
                    result.raise_for_status()
                    return result.json()
                except (httpx.HTTPStatusError, httpx.ConnectTimeout) as e:
                    last_exception = e
                    logger.warning(
                        f"Error calling API {method} at endpoint {endpoint}: {e}. Attempt {attempt + 1}"
                    )
                    sleep_with_backoff(attempt=attempt)

        msg = f"Too many API retries for {method} at endpoint {endpoint}. Last error {last_exception}."
        if isinstance(last_exception, httpx.HTTPStatusError):
            msg = msg + f" Response body {last_exception.response.text}"
        raise TooManyAPIRetriesError(msg)

    @log_performance
    def check_if_entity_has_results(
        self,
        entity_id: str,
        report_dates: ReportDates,
        similarity_text: str | None = None,
        *,
        source_filter: list[str] | None = None,
        sentiment_threshold: float | None = None,
        chunk_limit: int | None = 1,
        rerank_threshold: float | None = None,
    ) -> list[Result]:
        """
        Make a simple query to find if the entity has results.
        Based on this, the next steps will happen or not.
        """

        query = build_query(
            entity_id=entity_id,
            report_dates=report_dates,
            similarity_text=similarity_text,
            source_filter=source_filter,
            sentiment_threshold=sentiment_threshold,
            chunk_limit=chunk_limit,
            rerank_threshold=rerank_threshold,
            source_rank_boost=None,
            freshness_boost=None,
        )
        results = self.api_search(
            endpoint="/v1/search",
            method="POST",
            payload=query,
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
        similarity_text: str | None = None,
        topic: str | None = None,
        source_filter: list[str] | None = None,
        sentiment_threshold: float | None = settings.EXPLORATORY_SENTIMENT_THRESHOLD,
        chunk_limit: int | None = settings.API_CHUNKS_LIMIT_EXPLORATORY,
        rerank_threshold: float | None = settings.API_RERANK_EXPLORATORY,
        source_rank_boost: int | None = settings.API_SOURCE_RANK_BOOST,
        freshness_boost: int | None = settings.API_FRESHNESS_BOOST,
    ):
        query = build_query(
            entity_id=entity_id,
            report_dates=report_dates,
            similarity_text=similarity_text,
            source_filter=source_filter,
            sentiment_threshold=sentiment_threshold,
            chunk_limit=chunk_limit,
            rerank_threshold=rerank_threshold,
            source_rank_boost=source_rank_boost,
            freshness_boost=freshness_boost,
        )

        results = self.api_search(
            endpoint="/v1/search",
            method="POST",
            payload=query,
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
        topics: list[str],
        report_dates: ReportDates,
        executor: ThreadPoolExecutor,
        source_filter: list[str] | None = None,
        sentiment_threshold: float | None = settings.EXPLORATORY_SENTIMENT_THRESHOLD,
        chunk_limit: int | None = settings.API_CHUNKS_LIMIT_EXPLORATORY,
        use_topics: bool = True,
        rerank_threshold: float | None = settings.API_RERANK_EXPLORATORY,
        source_rank_boost: int | None = settings.API_SOURCE_RANK_BOOST,
        freshness_boost: int | None = settings.API_FRESHNESS_BOOST,
    ) -> list[Result]:
        if use_topics:
            # TODO use jinja2
            company_topics = [t.format(company=entity.name) for t in topics]
            futures = [
                executor.submit(
                    self._run_single_exploratory_search,
                    entity_id=entity.id,
                    similarity_text=similarity_text,
                    topic=topic,
                    report_dates=report_dates,
                    source_filter=source_filter,
                    sentiment_threshold=sentiment_threshold,
                    chunk_limit=chunk_limit,
                    rerank_threshold=rerank_threshold,
                    source_rank_boost=source_rank_boost,
                    freshness_boost=freshness_boost,
                    enable_metric=True,
                    metric_name=f"Exploratory search. Entity {entity.id}",
                )
                for similarity_text, topic in zip(company_topics, topics)
            ]
            # In addition to searching by topics, query with just the entity
            futures.append(
                executor.submit(
                    self._run_single_exploratory_search,
                    entity_id=entity.id,
                    report_dates=report_dates,
                    enable_metric=True,
                    metric_name=f"Exploratory search. Entity {entity.id}",
                )
            )
            # Remove duplicates and return as a list
            v = list(set(itertools.chain(*(f.result() for f in as_completed(futures)))))

            return v

        else:
            return self._run_single_exploratory_search(
                entity_id=entity.id,
                report_dates=report_dates,
                enable_metric=True,
                metric_name=f"Exploratory search. Entity {entity.id}",
            )

    def _run_follow_up_single_question(
        self,
        entity_id: str,
        question: str | None,
        report_dates: ReportDates,
        *,
        source_filter: list[str] | None = None,
        sentiment_threshold: float | None = settings.FOLLOWUP_SENTIMENT_THRESHOLD,
        chunk_limit: int | None = settings.API_CHUNK_LIMIT_FOLLOWUP,
        rerank_threshold: float | None = settings.API_RERANK_FOLLOWUP,
        source_rank_boost: int | None = settings.API_SOURCE_RANK_BOOST,
        freshness_boost: int | None = settings.API_FRESHNESS_BOOST,
    ):
        query = build_query(
            entity_id=entity_id,
            report_dates=report_dates,
            similarity_text=question,
            source_filter=source_filter,
            sentiment_threshold=sentiment_threshold,
            chunk_limit=chunk_limit,
            rerank_threshold=rerank_threshold,
            source_rank_boost=source_rank_boost,
            freshness_boost=freshness_boost,
        )

        results = self.api_search(
            endpoint="/v1/search",
            method="POST",
            payload=query,
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
        source_filter: list[str] | None,
        executor: ThreadPoolExecutor,
        source_rank_boost: int | None = settings.API_SOURCE_RANK_BOOST,
        freshness_boost: int | None = settings.API_FRESHNESS_BOOST,
    ) -> QAPairs:
        future_to_question = {
            executor.submit(
                self._run_follow_up_single_question,
                entity_id=entity.id,
                question=question,
                report_dates=report_dates,
                source_filter=source_filter,
                source_rank_boost=source_rank_boost,
                freshness_boost=freshness_boost,
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
    similarity_text: str | None,
    report_dates: ReportDates,
    *,
    source_filter: list[str] | None,
    sentiment_threshold: float | None,
    chunk_limit: int,
    rerank_threshold: float | None,
    source_rank_boost: int | None,
    freshness_boost: int | None,
) -> dict:
    if source_rank_boost is None:
        source_rank_boost = settings.API_SOURCE_RANK_BOOST
    if freshness_boost is None:
        freshness_boost = settings.API_FRESHNESS_BOOST
    query: SearchAPIQueryDict = {
        "auto_enrich_filters": False,  # Our queries are tuned, avoid extra unexpected filters
        "filters": {
            "timestamp": {
                "start": report_dates.start.isoformat(),
                "end": report_dates.end.isoformat(),
            }
        },
        "ranking_params": {
            "source_boost": source_rank_boost,
            "freshness_boost": freshness_boost,
        },
        "max_chunks": chunk_limit,
    }

    if similarity_text:
        query["text"] = similarity_text

    # Check if entity_id is presumably a known entity or a topic
    if len(entity_id) == 6:
        query["filters"]["entity"] = {"any_of": [entity_id]}
    else:
        raise ValueError(f"Invalid entity ID format: {entity_id}")

    # If a sentiment threshold is provided, filter for strong positive/negative
    # We want to avoid specifically chunks with sentiment 0 as those are often not relevant
    if sentiment_threshold:
        sentiment_threshold = abs(sentiment_threshold) # Ensure positive, we only care about magnitude
        query["filters"]["sentiment"] = {"ranges": [{"min": -1, "max": -sentiment_threshold}, {"min": sentiment_threshold, "max": 1}]}

    if rerank_threshold is None:
        query["ranking_params"]["reranker"] = {"enabled": False}
    else:
        query["ranking_params"]["reranker"] = {
            "enabled": True,
            "threshold": rerank_threshold,
        }

    # Use high-quality sources if desired
    if source_filter:
        query["filters"]["source"] = {"mode": "INCLUDE", "values": source_filter}

    return {"query": query}
