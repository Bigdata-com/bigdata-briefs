from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from hashlib import sha256
from importlib.metadata import version
from threading import Lock
from uuid import UUID

from bigdata_briefs import logger
from bigdata_briefs.api.models import BriefCreationRequest, WorkflowStatus
from bigdata_briefs.api.storage import StorageManager
from bigdata_briefs.attribution.sources import (
    consolidate_report_sources,
    create_sources_for_report,
    process_topic_collection,
    replace_references_in_topic_collection,
)
from bigdata_briefs.exceptions import (
    EmtpyWatchlistError,
    FailedBriefGenerationError,
)
from bigdata_briefs.llm_client import (
    LLMClient,
)
from bigdata_briefs.metrics import (
    BulletPointMetrics,
    CacheMetrics,
    ContentMetrics,
    EmbeddingsMetrics,
    LLMMetrics,
    QueryUnitMetrics,
)
from bigdata_briefs.models import (
    BriefReport,
    BulletPointsUsage,
    Entity,
    FollowUpAnalysis,
    IntroSection,
    NoInfoReportGenerationStep,
    QAPairs,
    ReportDates,
    ReportTitle,
    Result,
    RetrievedSources,
    SingleBulletPoint,
    SingleEntityReport,
    TopicCollection,
    ValidatedInput,
    Watchlist,
    WatchlistReport,
)
from bigdata_briefs.novelty.embedding_client import EmbeddingClient
from bigdata_briefs.novelty.novelty_service import NoveltyFilteringService
from bigdata_briefs.novelty.storage import EmbeddingStorage
from bigdata_briefs.prompts.prompt_loader import get_prompt_keys
from bigdata_briefs.prompts.user_prompts import (
    get_followup_questions_user_prompt,
    get_report_title_user_prompt,
    get_report_user_prompt,
    get_single_bullet_user_prompt,
)
from bigdata_briefs.query_service.sdk import (
    CheckIfThereAreResultsSearchConfig,
    ExploratorySearchConfig,
    QueryService,
)
from bigdata_briefs.settings import settings
from bigdata_briefs.storage import write_report_with_sources
from bigdata_briefs.tracing.service import TraceEventName, TracingService
from bigdata_briefs.utils import log_performance, log_time
from bigdata_briefs.weighted_semaphore import WeightedSemaphore

MIN_TOPICS_FOR_INTRO = 1
# We just want a number big enough to handle all connections, the limit is applied by SDK
# and by the Weighed semaphore
EXECUTOR_WORKERS = 10_000


class BriefPipelineService:
    def __init__(
        self,
        llm_client: LLMClient,
        query_service: QueryService,
        tracing_service: TracingService,
        novelty_filter_service: NoveltyFilteringService,
    ):
        self.novelty_filter_service = novelty_filter_service
        self.weighted_semaphore = WeightedSemaphore(settings.SDK_SIMULTANEOUS_REQUESTS)
        self.llm_client = llm_client
        self.query_service = query_service
        self.tracing_service = tracing_service
        self.lock = Lock()
        self.no_info_reports = []

    @log_performance
    def generate_follow_up_questions(
        self,
        entity: Entity,
        topics: list[str],
        report_dates: ReportDates,
        results: list[Result],
    ) -> list[str]:
        prompt_keys = get_prompt_keys("follow_up_questions")
        user_prompt = get_followup_questions_user_prompt(
            entity=entity,
            results=results,
            report_dates=report_dates,
            user_template=prompt_keys.user_template,
            topics=topics,
            response_format=f"{FollowUpAnalysis.model_json_schema()}",
        )
        # user_prompt += f"\n\nYour response should be a JSON object that matches the following schema:\n\n{FollowUpAnalysis.model_json_schema()}"
        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": "```json\n{"},
        ]

        follow_up_questions = self.llm_client.call_with_response_format(
            system=[{"role": "assistant", "content": prompt_keys.system_prompt}],
            messages=messages,
            text_format=FollowUpAnalysis,
            **prompt_keys.llm_kwargs,
        )

        return follow_up_questions.questions

    @log_performance
    def generate_new_report(
        self, entity: Entity, qa_pairs: QAPairs, report_dates: ReportDates
    ):
        report_sources, reverse_map = create_sources_for_report(qa_pairs)

        prompt_keys = get_prompt_keys("company_update")
        user_prompt = get_report_user_prompt(
            entity=entity,
            qa_pairs=qa_pairs,
            report_dates=report_dates,
            user_template=prompt_keys.user_template,
            response_format=f"{TopicCollection.model_json_schema()}",
            report_sources=report_sources,
        )
        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": "```json\n{"},
        ]

        collection = self.llm_client.call_with_response_format(
            system=[{"role": "assistant", "content": prompt_keys.system_prompt}],
            messages=messages,
            text_format=TopicCollection,
            **prompt_keys.llm_kwargs,
        )

        updated_collection = replace_references_in_topic_collection(
            collection, reverse_map, entity
        )

        report = process_topic_collection(updated_collection, report_sources)

        return (
            SingleEntityReport(
                entity_id=entity.id,
                entity_info=entity.to_entity_info().model_dump(exclude_none=True),
                report_bulletpoints=report.topics,
                relevance_score=report.relevance_score,
                clean_final_report="",  # TODO this is using the financial info of the bulletpoint (RENAME)
            ),
            report_sources,
        )

    def create_no_info_report(self, entity: Entity, message: str, generation_step: str):
        with self.lock:
            self.no_info_reports.append((entity, generation_step))

        return (
            SingleEntityReport(
                entity_id=entity.id,
                entity_info=entity.to_entity_info().model_dump(exclude_none=True),
                report_bulletpoints=[message],
                relevance_score=[1],
                clean_final_report="",
                is_no_info_report=True,
            ),
            {},
        )

    def execute_entity_report_pipeline(
        self,
        entity: Entity,
        topics: list[str],
        source_filter: list[str] | None,
        report_dates: ReportDates,
        executor: ThreadPoolExecutor,
    ) -> tuple[SingleEntityReport, RetrievedSources]:
        logger.debug(f"Starting report on {entity}")

        if source_filter:
            any_result_search_config = CheckIfThereAreResultsSearchConfig(
                source_filter=source_filter
            )
            exploratory_search_config = ExploratorySearchConfig(
                source_filter=source_filter
            )
        else:
            any_result_search_config = CheckIfThereAreResultsSearchConfig()
            exploratory_search_config = ExploratorySearchConfig()
        # Quick initial search to check if there are any results
        initial_results = self.query_service.check_if_entity_has_results(
            entity_id=entity.id,
            report_dates=report_dates,
            config=any_result_search_config,
        )

        if not initial_results:
            logger.debug(f"No results found in initial search for {entity}")
            return self.create_no_info_report(
                entity,
                message=f"No new information to report on {entity.name}.",
                generation_step=NoInfoReportGenerationStep.BEFORE_EXPLORATORY_SEARCH,
            )

        # If we found results, proceed with full exploratory search
        with self.weighted_semaphore(len(topics) + 1):
            exploratory_search_results = self.query_service.run_exploratory_search(
                entity=entity,
                topics=topics,
                report_dates=report_dates,
                executor=executor,
                enable_metric=True,
                metric_name="Exploratory search. All entities",
                config=exploratory_search_config,
            )
        if not exploratory_search_results:
            logger.debug(f"No new information found for {entity}")
            return self.create_no_info_report(
                entity,
                message=f"No new information to report on {entity.name}. Sadge.",
                generation_step=NoInfoReportGenerationStep.EXPLORATORY_SEARCH,
            )

        follow_up_questions = self.generate_follow_up_questions(
            entity,
            topics,
            report_dates,
            exploratory_search_results,
            enable_metric=True,
            metric_name="Generate follow up questions",
        )
        if not follow_up_questions:
            logger.debug(f"No follow-up questions generated for {entity}")
            return self.create_no_info_report(
                entity,
                message=f"No new information to report on {entity.name}. Sadge.",
                generation_step=NoInfoReportGenerationStep.FOLLOW_UP_QUESTIONS,
            )

        if len(follow_up_questions) != settings.LLM_FOLLOW_UP_QUESTIONS:
            logger.debug(f"Number of followup questions: {len(follow_up_questions)}")

        with self.weighted_semaphore(len(follow_up_questions)):
            qa_pairs = self.query_service.run_query_with_follow_up_questions(
                entity=entity,
                follow_up_questions=follow_up_questions,
                report_dates=report_dates,
                executor=executor,
                enable_metric=True,
                metric_name="Run follow up questions",
                source_filter=source_filter,
            )
        if not any(pair.answer for pair in qa_pairs.pairs):
            logger.debug(f"No qa-pairs generated for {entity}")
            return self.create_no_info_report(
                entity,
                message=f"No new information to report on {entity.name}.",
                generation_step=NoInfoReportGenerationStep.QA_PAIRS,
            )

        entity_report, source_mapping = self.generate_new_report(
            entity,
            qa_pairs,
            report_dates,
            enable_metric=True,
            metric_name="Generating report",
        )
        BulletPointMetrics.track_usage(
            BulletPointsUsage(
                bullet_points_before_novelty=len(entity_report.report_bulletpoints)
            )
        )
        if settings.NOVELTY_ENABLED and report_dates.novelty:
            # Filter final report for novelty
            novel_bulletpoints = self.novelty_filter_service.filter_by_novelty(
                texts=entity_report.report_bulletpoints,
                entity_id=entity_report.entity_id,
                start_date=report_dates.get_novelty_dates().start,
                end_date=report_dates.get_novelty_dates().end,
                current_date=report_dates.end,
                clean_up_func=SingleEntityReport.remove_references,
            )
            novel_titles = [bp.original_text for bp in novel_bulletpoints]

            # To ensure that the length matches, we need to remove unwanted bp from the report
            rp_bulletpoints = []
            relevance_scores = []

            for i, title in enumerate(entity_report.report_bulletpoints):
                if title in novel_titles:
                    rp_bulletpoints.append(title)
                    relevance_scores.append(entity_report.relevance_score[i])

            entity_report.relevance_score = relevance_scores
            entity_report.report_bulletpoints = rp_bulletpoints
        else:
            logger.info(
                "Skipping novelty filtering.",
                entity_id=entity_report.entity_id,
                is_enabled=report_dates.novelty,
            )

        if len(entity_report.relevance_score) != len(entity_report.report_bulletpoints):
            logger.error(
                f"Length missmatch between relevance_score and bulletpoints. "
                f"{len(entity_report.relevance_score)} != {len(entity_report.report_bulletpoints)}"
            )

        # Filter by section relevance score
        bulletpoint_score_pairs = [
            (bulletpoint, score)
            for bulletpoint, score in zip(
                entity_report.report_bulletpoints, entity_report.relevance_score
            )
            if score > settings.INTRO_SECTION_MIN_RELEVANCE_SCORE
        ]

        # Sort by relevance score (highest first)
        sorted_pairs = sorted(bulletpoint_score_pairs, key=lambda x: x[1], reverse=True)

        # Extract bulletpoints and scores from sorted pairs
        if sorted_pairs:
            entity_report.report_bulletpoints = [pair[0] for pair in sorted_pairs]
            entity_report.relevance_score = [pair[1] for pair in sorted_pairs]
        else:
            entity_report.report_bulletpoints = []
            entity_report.relevance_score = []

        if not entity_report.report_bulletpoints:
            return self.create_no_info_report(
                entity,
                message=f"No new information to report on {entity.name}.",
                generation_step=NoInfoReportGenerationStep.NOVELTY,
            )

        # Format to bulletpoints text
        clean_final_reports = [f"* {rp} \n" for rp in entity_report.report_bulletpoints]

        entity_report.clean_final_report = "".join(clean_final_reports)

        for doc_id in source_mapping.keys():
            if doc_id in entity_report.clean_final_report:
                source_mapping.get(doc_id).mark_as_used()

        return entity_report, source_mapping

    @log_performance
    def generate_intro_section_single_bullet_point(
        self,
        company_report: SingleEntityReport,
        report_dates: ReportDates,
    ) -> str:
        """Generate a single bullet point for a company report."""
        prompt_keys = get_prompt_keys("intro_section")
        user_prompt = get_single_bullet_user_prompt(
            company_report=company_report,
            user_template=prompt_keys.user_template,
            report_dates=report_dates,
            response_format=f"{SingleBulletPoint.model_json_schema()}",
        )
        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": "```json\n{"},
        ]

        struct_response = self.llm_client.call_with_response_format(
            system=[{"role": "assistant", "content": prompt_keys.system_prompt}],
            messages=messages,
            text_format=SingleBulletPoint,
            **prompt_keys.llm_kwargs,
        )
        return struct_response.bullet_point

    @log_performance
    def generate_intro_section_bullets(
        self,
        actionable_company_reports: list[SingleEntityReport],
        report_dates: ReportDates,
        executor: ThreadPoolExecutor,
    ) -> list[str]:
        """Generate bullet points for top companies in parallel."""
        if len(actionable_company_reports) < MIN_TOPICS_FOR_INTRO:
            return []

        # Take only the top companies based on the setting
        top_companies = actionable_company_reports[
            : settings.MAX_INTRO_SECTION_COMPANIES
        ]

        # Generate bullet points in parallel
        futures_to_company = {
            executor.submit(
                self.generate_intro_section_single_bullet_point,
                company_report,
                report_dates,
            ): company_report
            for company_report in top_companies
        }

        bullet_points = []
        for future in futures_to_company:
            try:
                bullet_point = future.result()
                bullet_points.append(bullet_point)
            except Exception as e:
                company = futures_to_company[future]
                company_name = company.entity_info.get("name", "Unknown")
                logger.warning(
                    f"Failed to generate bullet point for {company_name}: {e}"
                )

        return bullet_points

    @log_performance
    def generate_report_title(
        self,
        first_bullet_point: str,
        report_dates: ReportDates,
    ) -> str:
        """Generate a report title based on the first bullet point."""
        prompt_keys = get_prompt_keys("report_title")
        user_prompt = get_report_title_user_prompt(
            first_bullet_point=first_bullet_point,
            user_template=prompt_keys.user_template,
            report_dates=report_dates,
            response_format=f"{ReportTitle.model_json_schema()}",
        )
        messages = [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": "```json\n{"},
        ]

        struct_response = self.llm_client.call_with_response_format(
            system=[{"role": "assistant", "content": prompt_keys.system_prompt}],
            messages=messages,
            text_format=ReportTitle,
            **prompt_keys.llm_kwargs,
        )
        return struct_response.report_title

    @log_performance
    def generate_intro_section_and_title(
        self,
        actionable_company_reports: list[SingleEntityReport],
        report_dates: ReportDates,
        executor: ThreadPoolExecutor,
    ) -> IntroSection:
        """Generate intro section with individual bullet points and a title."""
        # Generate bullet points for top companies in parallel
        bullet_points = self.generate_intro_section_bullets(
            actionable_company_reports, report_dates, executor
        )

        if not bullet_points:
            return IntroSection(intro_section="", report_title="You are up to date")

        # Create intro section from bullet points
        intro_section = "\n\n".join(bullet_points)

        # Generate title based on the first bullet point
        report_title = self.generate_report_title(bullet_points[0], report_dates)

        return IntroSection(intro_section=intro_section, report_title=report_title)

    @log_performance
    def execute_watchlist_report_pipeline(
        self,
        entities: list[Entity],
        watchlist: Watchlist,
        topics: list[str],
        source_filter: list[str] | None,
        report_dates: ReportDates,
        request_id: UUID,
        storage_manager: StorageManager,
    ) -> tuple[WatchlistReport, RetrievedSources]:
        storage_manager.log_message(request_id, "Generating report per entity")
        with ThreadPoolExecutor(max_workers=EXECUTOR_WORKERS) as executor:
            futures_to_entity = {
                executor.submit(
                    self.execute_entity_report_pipeline,
                    entity,
                    topics,
                    source_filter,
                    report_dates,
                    executor,
                ): entity
                for entity in entities
            }

            entity_reports: list[SingleEntityReport] = []
            # Aggregate and consolidate sources for all entities
            source_metadata = RetrievedSources(root={})
            entity_reports_failed = []
            for future in as_completed(futures_to_entity):
                entity = futures_to_entity[future]
                try:
                    entity_report, sources_per_entity = future.result()
                    logger.debug(f"Finished for {entity}")
                    entity_reports.append(entity_report)

                    if sources_per_entity:
                        consolidate_report_sources(source_metadata, sources_per_entity)
                except Exception as e:
                    entity_reports_failed.append(entity)
                    logger.warning(
                        f"Unhandled error occurred generating entity report '{futures_to_entity[future].name}'. The entity will be ignored: {str(e)}"
                    )

            if len(entity_reports_failed) == len(entities):
                logger.error(
                    f"All entities failed to generate reports: {entity_reports_failed} with an unexpected error!"
                )
                raise FailedBriefGenerationError(
                    "All entities failed to generate a report."
                )

            entity_reports_with_info = [
                rep for rep in entity_reports if not rep.is_no_info_report()
            ]

            # Sort entity reports by relevance score (highest first)
            entity_reports_with_info = sorted(
                entity_reports_with_info,
                key=lambda report: calculate_relevance_score(report.relevance_score),
                reverse=True,
            )
            storage_manager.log_message(
                request_id,
                f"Generated reports for {len(entities)} entities, {len(entity_reports_with_info)} with information, {len(self.no_info_reports)} without information and {len(entity_reports_failed)} failed.",
            )
            storage_manager.log_message(request_id, "Generating introduction section")
            intro_section = self.generate_intro_section_and_title(
                actionable_company_reports=entity_reports_with_info,
                report_dates=report_dates,
                executor=executor,
            )
            storage_manager.log_message(request_id, "Introduction section generated")
        # Construct the final WatchlistReport
        return (
            WatchlistReport(
                watchlist_id=watchlist.id,
                watchlist_name=watchlist.name,
                report_title=intro_section.report_title,
                report_date=report_dates.end,
                introduction=intro_section.intro_section,
                entity_reports=entity_reports_with_info,
            ),
            source_metadata,
        )

    @classmethod
    def factory(
        cls,
        query_service: QueryService,
        tracing_service: TracingService,
        embedding_storage: EmbeddingStorage,
    ):
        embedding_storage = embedding_storage
        embedding_client = EmbeddingClient(settings.NOVELTY_MODEL)
        novelty_filter_service = NoveltyFilteringService(
            embedding_client, embedding_storage
        )
        llm_client = LLMClient()
        return cls(llm_client, query_service, tracing_service, novelty_filter_service)

    @log_time
    def generate_brief(
        self,
        record: BriefCreationRequest,
        request_id: UUID,
        storage_manager: StorageManager,
    ) -> BriefReport:
        try:
            storage_manager.update_status(request_id, WorkflowStatus.IN_PROGRESS)
            workflow_execution_start = datetime.now()
            storage_manager.log_message(request_id, "Validating input parameters")
            record_data = self.parse_and_validate(record, request_id, storage_manager)

            (
                watchlist_report,
                source_metadata,
            ) = self.execute_watchlist_report_pipeline(
                record_data.entities,
                record_data.watchlist,
                record_data.topics,
                record_data.sources_filter,
                record_data.report_dates,
                enable_metric=True,
                metric_name="Execute watchlist report pipeline",
                request_id=request_id,
                storage_manager=storage_manager,
            )

            n_watchlist_items = len(record_data.entities)
            n_no_info_reports = len(self.no_info_reports)
            llm_metrics = LLMMetrics.get_total_usage()
            bp_metrics = BulletPointMetrics.get_total_usage()
            embedding_metrics = EmbeddingsMetrics.get_total_usage()
            content_metrics = ContentMetrics.get_total_usage()

            document_aggregation = {
                f"documents_for_topic_{k.replace(' ', '_')}": v.total_documents
                for k, v in content_metrics.items()
            }
            chunk_aggregation = {
                f"chunks_for_topic_{k.replace(' ', '_')}": v.total_chunks
                for k, v in content_metrics.items()
            }

            total_chunks = sum(v.total_chunks for v in content_metrics.values())
            total_documents = sum(v.total_documents for v in content_metrics.values())

            novelty_date_range = (
                record_data.report_dates.get_novelty_dates().get_lookback_days()
                if record_data.report_dates.novelty
                else 0
            )
            logger.debug(
                "Summary of metrics",
                total_prompt_tokens=llm_metrics.prompt_tokens,
                total_completion_tokens=llm_metrics.completion_tokens,
                total_tokens=llm_metrics.total_tokens,
                total_llm_calls=llm_metrics.n_calls,
                total_embedding_tokens=embedding_metrics.tokens,
                n_watchlist_items=n_watchlist_items,
                n_entity_reports=n_watchlist_items - n_no_info_reports,
                n_no_info_reports=n_no_info_reports,
                no_info_reports=self.no_info_reports,
                total_bp_before_novelty=bp_metrics.bullet_points_before_novelty,
                total_bp_after_novelty=bp_metrics.bullet_points_after_novelty,
                total_bp_stored=bp_metrics.bullet_points_stored,
                brief_date_range=record_data.report_dates.get_lookback_days(),
                novelty_date_range=novelty_date_range,
                retrieved_from_cache=CacheMetrics.get_total_usage(),
                query_units_consumed=QueryUnitMetrics.get_total_usage(),
                **document_aggregation,
                **chunk_aggregation,
            )

            pipeline_output = BriefReport.from_watchlist_report(
                watchlist_report,
                source_metadata,
                novelty=record_data.report_dates.novelty,
            )

            if pipeline_output.is_empty:
                logger.debug(f"No new news for {record_data.watchlist.id}.")
            workflow_execution_end = datetime.now()
            self.tracing_service.send_trace(
                event_name=TraceEventName.REPORT_GENERATED,
                trace={
                    "bigdataClientVersion": version("bigdata-client"),
                    "workflowUsage": QueryUnitMetrics.get_total_usage(),
                    "workflowStartDate": workflow_execution_start.isoformat(
                        timespec="seconds"
                    ),
                    "workflowEndDate": workflow_execution_end.isoformat(
                        timespec="seconds"
                    ),
                    "watchlistLength": len(record_data.entities),
                    "numberOfEntityReports": len(watchlist_report.entity_reports),
                    "numberOfNoInfoReports": n_no_info_reports,
                    "numberOfChunks": total_chunks,
                    "numberOfDocuments": total_documents,
                },
            )
            storage_manager.log_message(request_id, "Storing output report")
            write_report_with_sources(
                request_id, pipeline_output, storage_manager.db_session
            )
            storage_manager.update_status(request_id, WorkflowStatus.COMPLETED)
            return pipeline_output
        except Exception as e:
            storage_manager.update_status(request_id, WorkflowStatus.FAILED)
            storage_manager.log_message(request_id, str(e))
            raise

    def parse_and_validate(
        self,
        record: BriefCreationRequest,
        request_id: UUID,
        storage_manager: StorageManager,
    ) -> ValidatedInput:
        logger.debug(record)

        # Ensure all topics include the placeholder {company}
        topics = record.topics or settings.TOPICS

        for topic in topics:
            if "{company}" not in topic:
                raise ValueError(
                    f"Invalid topic '{topic}'. Topics must include '{{company}}'."
                )

        if isinstance(record.companies, str):
            watchlist = self.query_service.get_watchlist(watchlist_id=record.companies)
            if not watchlist.items:
                raise EmtpyWatchlistError(
                    f"Validation failed before removing non-companies {watchlist.id}"
                )

            if len(watchlist.items) > settings.WATCHLIST_ITEMS_LIMIT:
                watchlist.items = set(
                    list(watchlist.items)[: settings.WATCHLIST_ITEMS_LIMIT]
                )
                company_limit_msg = f"Watchlist {watchlist.id} has too many items: {len(watchlist.items)} Taking the first {settings.WATCHLIST_ITEMS_LIMIT}"
                logger.debug(company_limit_msg)
                storage_manager.log_message(request_id, company_limit_msg)

            entity_ids = list(watchlist.items)
        elif isinstance(record.companies, list):
            entity_ids = record.companies
            # Use a dummy watchlist as the whole workflow expects a watchlist ID and name
            watchlist = Watchlist(
                id=f"custom_{sha256(str(record.companies)).hexdigest()}",
                name="Custom set of entities",
            )
        else:
            raise ValueError(
                "Companies must be either a list of RP entity IDs or a string representing a watchlist ID."
            )

        # Ensure there is entities, there is no duplicates and all entities are companies
        entities = self.query_service.get_entities(entity_ids)

        dedupped_entities = {c.id: c for c in entities}

        entities = list(dedupped_entities.values())

        if len(entities) == 0:
            raise ValueError("No entities found in the provided universe or watchlist.")

        logger.debug("Entities recovered")
        entities = remove_non_companies(entities=entities)
        if len(entities) == 0:
            raise EmtpyWatchlistError(
                f"Validation failed after removing non-companies {watchlist.id}"
            )

        return ValidatedInput(
            watchlist=Watchlist(
                id=watchlist.id,
                name=watchlist.name,
            ),
            entities=entities,
            topics=topics,
            sources_filter=record.sources,
            report_dates=ReportDates(
                start=record.report_start_date,
                end=record.report_end_date,
                novelty=record.novelty,
            ),
        )


def remove_non_companies(entities: list[Entity]):
    for item in entities[:]:
        if item.entity_type != "COMP":
            entities.remove(item)

    return entities


def calculate_relevance_score(score_values: list[int]) -> float:
    """
    Calculate a relevance score using strict-dominance geometric weighting algorithm.

    This function implements a scoring system where higher individual scores always dominate
    multiple lower scores, preventing gaming through quantity over quality. The algorithm
    sorts scores in descending order and applies geometric decay weighting.

    Mathematical Formula:
        For scores [s₁, s₂, s₃, ...] sorted in descending order:
        result = s₁ × 1.0 + s₂ × 0.10 + s₃ × 0.01 + s₄ × 0.001 + ...

        Where each subsequent weight = previous_weight × DECAY_FACTOR (0.10)

    Strict Dominance Property:
        A single score of value N will always produce a higher result than any number
        of scores with values < N, due to the geometric decay ensuring the first score
        dominates all subsequent contributions.

    Performance Optimization:
        Computation stops early when weights become smaller than 1e-6 threshold,
        avoiding unnecessary calculations for negligible contributions.

    Examples:
        >>> calculate_relevance_score([3, 8, 5])  # Order doesn't matter
        8.53  # 8x1.0 + 5x0.10 + 3x0.01
    """
    DECAY_FACTOR = 0.10  # Geometric decay factor for scoring algorithm
    EARLY_EXIT_THRESHOLD = 1e-6  # Minimum weight threshold for computation

    # Early return for empty input
    if not score_values:
        return 0.0

    # Sort scores in descending order for geometric weighting
    sorted_scores = sorted(score_values, reverse=True)

    # Calculate weighted sum with geometric decay
    total_weighted_score = 0.0
    current_weight = 1.0

    for individual_score in sorted_scores:
        total_weighted_score += individual_score * current_weight
        current_weight *= DECAY_FACTOR

        # Early exit when weights become negligible
        if current_weight < EARLY_EXIT_THRESHOLD:
            break

    return total_weighted_score
