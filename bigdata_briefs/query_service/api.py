import itertools
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Semaphore

import httpx
from bigdata_client import Bigdata
from bigdata_client.models.watchlists import Watchlist
from pydantic import ValidationError

from bigdata_briefs import logger
from bigdata_briefs.exceptions import TooManySDKRetriesError
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
from bigdata_briefs.settings import settings
from bigdata_briefs.utils import (
    log_args,
    log_performance,
    log_return_value,
    log_time,
    sleep_with_backoff,
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
            base_url=settings.API_BASE_URL, headers=self.headers
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
        results = self._call_api(
            endpoint="/v1/knowledge-graph/entities/id",
            method="POST",
            payload={"values": entity_ids},
            headers=self.headers,
        )
        raw_entities = results
        entities = []
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
        e = None
        with self.semaphore:
            for attempt in range(settings.API_RETRIES):
                try:
                    result = self._client.request(
                        method=method, url=endpoint, json=payload, headers=headers
                    )
                    result.raise_for_status()
                    return result.json()
                except Exception as e:
                    logger.warning(
                        f"Error calling API {method} at endpoint {endpoint}: {e}. Attempt {attempt + 1}"
                    )
                    sleep_with_backoff(attempt=attempt)

        raise TooManySDKRetriesError(
            f"Too many API retries for {method} at endpoint {endpoint}. Last error {e}"
        )

    @log_performance
    def check_if_entity_has_results(
        self,
        entity_id: str,
        report_dates: ReportDates,
        similarity_text: str | None = None,
        *,
        source_filter: list[str] | None = None,
        sentiment_threshold: float | None = None,
        chunk_limit: int | None = None,
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
        chunk_limit: int | None = None,
        rerank_threshold: float | None = settings.API_RERANK_EXPLORATORY,
    ):
        query = build_query(
            entity_id=entity_id,
            report_dates=report_dates,
            similarity_text=similarity_text,
            source_filter=source_filter,
            sentiment_threshold=sentiment_threshold,
            chunk_limit=chunk_limit,
            rerank_threshold=rerank_threshold,
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
        chunk_limit: int | None = None,
        use_topics: bool = True,
        rerank_threshold: float | None = settings.API_RERANK_EXPLORATORY,
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
        chunk_limit: int | None = None,
        rerank_threshold: float | None = settings.API_RERANK_FOLLOWUP,
    ):
        query = build_query(
            entity_id=entity_id,
            report_dates=report_dates,
            similarity_text=question,
            source_filter=source_filter,
            sentiment_threshold=sentiment_threshold,
            chunk_limit=chunk_limit,
            rerank_threshold=rerank_threshold,
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
    ) -> QAPairs:
        future_to_question = {
            executor.submit(
                self._run_follow_up_single_question,
                entity_id=entity.id,
                question=question,
                report_dates=report_dates,
                source_filter=source_filter,
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
) -> dict:
    query: SearchAPIQueryDict = {
        "auto_enrich_filters": False, # Our queries are tuned, avoid extra unexpected filters
        "filters": {
            "timestamp": {
                "start": report_dates.start.isoformat(),
                "end": report_dates.end.isoformat(),
            }
        },
        "ranking_params": {
            "source_boost": 10,
            "freshness_boost": 8,
        },
        "max_results": chunk_limit,
    }

    if similarity_text:
        query["text"] = similarity_text

    # Check if entity_id is presumably a known entity or a topic
    if len(entity_id) == 6:
        query["filters"]["entity"] = {"any_of": [entity_id]}
    else:
        raise ValueError(f"Invalid entity ID format: {entity_id}")

    # If a sentiment threshold is provided, filter for strong positive/negative
    if sentiment_threshold:
        if 1 >= sentiment_threshold >= 0.1:
            sentiment = "positive"
        elif -1 <= sentiment_threshold <= -0.1:
            sentiment = "negative"
        elif -0.1 < sentiment_threshold < 0.1:
            sentiment = "neutral"

        query["filters"]["sentiment"] = {"values": [sentiment]}

    if rerank_threshold is None:
        query["ranking_params"]["reranker"] = {"enabled": False}
    else:
        # No way to change the reranker now
        pass

    # Use high-quality sources if desired
    if source_filter is not None:
        query["filters"]["source"] = {"mode": "INCLUDE", "values": source_filter}

    return {"query": query}
