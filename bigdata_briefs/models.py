import re
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Annotated, Any

from jinja2 import Template
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
)

from bigdata_briefs import logger
from bigdata_briefs.settings import settings
from bigdata_briefs.templates import loader

MAX_CHUNKS_PER_DOCUMENT = 10
REFERENCE_REGEX = re.compile(r"`:ref\[LIST:\[.*?\]\]`")


class NoInfoReportGenerationStep(StrEnum):
    BEFORE_EXPLORATORY_SEARCH = "BEFORE_EXPLORATORY_SEARCH"
    EXPLORATORY_SEARCH = "EXPLORATORY_SEARCH"
    FOLLOW_UP_QUESTIONS = "FOLLOW_UP_QUESTIONS"
    QA_PAIRS = "QA_PAIRS"
    NOVELTY = "NOVELTY"


class Watchlist(BaseModel):
    id: str
    name: str


class Entity(BaseModel):
    id: str
    name: str
    entity_type: str
    ticker: Annotated[str | None, Field(default=None, validation_alias="metadata_1")]

    _raw: Any = None  # Field used to keep the original response from SDK

    @classmethod
    def from_sdk(cls, sdk_entity):
        raw = sdk_entity
        instance = cls.model_validate(sdk_entity.model_dump())
        instance._raw = raw
        return instance

    def get_raw(self):
        return self._raw

    def to_entity_info(self):
        raw = self.get_raw()
        return EntityInfo(
            id=self.id,
            name=self.name,
            description=raw.description,
            entity_type=raw.entity_type,
            company_type=raw.company_type,
            country=raw.country,
            sector=raw.sector,
            industry_group=raw.industry_group,
            industry=raw.industry,
            ticker=raw.ticker,
            webpage=raw.webpage,
            isin_values=raw.isin_values,
            cusip_values=raw.cusip_values,
            sedol_values=raw.sedol_values,
            listing_values=raw.listing_values,
        )


class ChunkHighlight(BaseModel):
    pnum: int = Field(description="Paragraph number")
    snum: int = Field(description="Sentence number")


class Chunk(BaseModel):
    """Represents a snippet of text from a single result document."""

    text: str
    chunk: int
    relevance: float
    sentiment: float
    highlights: list[ChunkHighlight]

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_sdk(cls, sdk_chunk):
        return cls(
            text=sdk_chunk.text,
            chunk=sdk_chunk.chunk,
            relevance=sdk_chunk.relevance,
            sentiment=sdk_chunk.sentiment,
            highlights=[
                ChunkHighlight(pnum=sentence.paragraph, snum=sentence.sentence)
                for sentence in sdk_chunk.sentences
            ],
        )

    def __hash__(self) -> int:
        return hash((self.text, self.chunk))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Chunk):
            return (self.text, self.chunk) == (other.text, other.chunk)
        return NotImplemented


class Result(BaseModel):
    """Represents a single search result."""

    document_id: str
    headline: str
    timestamp: str
    source_key: str
    source_name: str
    source_rank: int | None = None
    url: str | None = None
    ts: str
    document_scope: str
    language: str
    chunks: tuple[Chunk, ...]

    model_config = ConfigDict(frozen=True)

    @field_validator("chunks", mode="after")
    @classmethod
    def filter_and_sort(cls, chunks):
        return tuple(sorted(chunks[:MAX_CHUNKS_PER_DOCUMENT], key=lambda x: x.chunk))

    @classmethod
    def from_sdk(cls, sdk_document):
        return cls(
            document_id=sdk_document.id,
            headline=sdk_document.headline,
            timestamp=sdk_document.timestamp.strftime("%Y-%m-%d %H:%M %Z"),
            source_name=sdk_document.source.name,
            source_key=sdk_document.source.key,
            source_rank=sdk_document.source.rank,
            url=sdk_document.url,
            ts=sdk_document.timestamp.isoformat(),
            document_scope=sdk_document.document_scope,
            language=sdk_document.language,
            chunks=[Chunk.from_sdk(sdk_chunk) for sdk_chunk in sdk_document.chunks],
        )


class StartEndDate(BaseModel):
    start: datetime
    end: datetime

    def get_lookback_days(self):
        return (self.end - self.start).days


class ReportDates(StartEndDate):
    novelty: bool

    def get_novelty_dates(self):
        if not self.novelty:
            raise ValueError(
                "get_novelty_start_date can't be calculated if novelty==false"
            )

        return StartEndDate(
            start=self.start - timedelta(days=settings.NOVELTY_LOOKBACK_DAYS),
            end=self.start,
        )


class ValidatedInput(BaseModel):
    watchlist: Watchlist
    entities: list[Entity]
    topics: list[str]
    report_dates: ReportDates
    sources_filter: list[str] | None


class FollowUpAnalysis(BaseModel):
    """Generates a list of follow-up questions for further analysis focusing on the most recent news (optional)."""

    questions: list[str] | None = Field(
        description="A list of short, actionable, fully contextualized follow-up questions. (no longer than 12 words).",
    )


class SourceChunkReference(BaseModel):
    ref_id: int
    document_id: str
    headline: str
    ts: str
    document_scope: str
    language: str
    source_key: str
    source_name: str
    source_rank: int | None = None
    url: str | None = None
    chunk_id: int
    text: str
    highlights: list[ChunkHighlight]
    _is_referenced: bool = False

    def is_referenced(self):
        return self._is_referenced

    def mark_as_used(self):
        self._is_referenced = True


class ReportedSources(RootModel):
    root: dict[
        str, SourceChunkReference
    ]  # The key is the reference ID and the value includes everything needed to reference the source


class RetrievedSources(ReportedSources):
    root: dict[
        str, SourceChunkReference
    ]  # The key is the reference ID and the value includes everything needed to reference the source

    def keys(self):
        """Return the keys of the underlying dictionary."""
        return self.root.keys()

    def values(self):
        """Return the values of the underlying dictionary."""
        return self.root.values()

    def items(self):
        """Return the items of the underlying dictionary."""
        return self.root.items()

    def get(self, key):
        """Get a value from the underlying dictionary."""
        return self.root.get(key)

    def set(self, key, value):
        """Set a value in the underlying dictionary."""
        self.root[key] = value

    @model_serializer
    def serialize(self):
        """
        Serialize only used references into a Python dict.
        """
        serialized_data = {
            ref_id: doc.model_dump()
            for ref_id, doc in self.items()
            if doc.is_referenced()
        }

        return serialized_data


class QuestionAnswer(BaseModel):
    question: str
    answer: list[Result] = []

    def render_md(self) -> str:
        return self._get_template().render(question=self.question, answer=self.answer)

    def render_with_references(self, report_sources: RetrievedSources):
        """Render the Q&A using reference IDs instead of document IDs."""
        return self._get_template().render(
            question=self.question,
            answer=self.answer,
            report_sources=report_sources.root,
        )

    def _get_template(self) -> Template:
        return loader.get_template("prompts/qa.md.jinja")


class QAPairs(BaseModel):
    """Collection of Q&A pairs for a single company."""

    pairs: list[QuestionAnswer]

    def render_md(self) -> str:
        """Render all Q&A pairs in Markdown, separated by '---'."""
        if not self.pairs:
            return "No new information to report."

        sections = [pair.render_md() for pair in self.pairs if pair.answer]
        return (
            "\n\n---\n\n".join(sections)
            if sections
            else "No new information to report."
        )

    def render_md_with_references(self, report_sources: RetrievedSources):
        """Render all Q&A pairs with reference IDs."""
        if not self.pairs:
            return "No new information to report."

        sections = [
            pair.render_with_references(report_sources)
            for pair in self.pairs
            if pair.answer
        ]
        return "\n\n---\n\n".join(sections)


class EntityInfo(BaseModel):
    """Model representing entity information for companies in briefs reports"""

    id: str
    name: str
    description: str | None = None
    entity_type: str | None = None
    company_type: str | None = None
    country: str | None = None
    sector: str | None = None
    industry_group: str | None = None
    industry: str | None = None
    gender: str | None = None
    ticker: str | None = None
    webpage: str | None = None
    isin_values: list[str] | None = None
    cusip_values: list[str] | None = None
    sedol_values: list[str] | None = None
    listing_values: list[str] | None = None
    market_cap: str | None = None


class SingleEntityReport(BaseModel):
    """A single entity report."""

    entity_id: str
    entity_info: dict  # EntityInfo has a lot of None values, we don't want to include them in the database that is why we dump with excude_none=True
    report_bulletpoints: Annotated[list[str], Field(exclude=True)] = []
    relevance_score: Annotated[list[int], Field(exclude=True)] = []
    clean_final_report: str

    _is_no_info_report: bool

    def __init__(self, is_no_info_report: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._is_no_info_report = is_no_info_report

    def is_no_info_report(self):
        if not self.clean_final_report and not self._is_no_info_report:
            logger.error(
                f"Clean final report is empty, but no_info_report is False => {self}"
            )
        return self._is_no_info_report or not self.clean_final_report

    @staticmethod
    def remove_references(text: str) -> str:
        """
        Cleans the input text by removing inline source attributions in the format `:ref[LIST[...]]`.

        >>> SingleEntityReport.remove_references("This is a test `:ref[LIST[1]]`")
        'This is a test '

        >>> SingleEntityReport.remove_references("This is a second test")
        'This is a second test'
        """
        return REFERENCE_REGEX.sub("", text)

    @staticmethod
    def _extract_references(text: str) -> tuple[str, list[str]]:
        """
        Extracts inline source attributions in the format `:ref[LIST[...]]` from text.

        Returns a tuple of (cleaned_text, list_of_references).

        >>> SingleEntityReport.extract_references("This is a test `:ref[LIST[1]]`")
        ('This is a test ', [':ref[LIST[1]]'])

        >>> SingleEntityReport.extract_references("Text `:ref[LIST[1]]` and `:ref[LIST[2]]` more text")
        ('Text  and  more text', [':ref[LIST[1]]', ':ref[LIST[2]]'])

        >>> SingleEntityReport.extract_references("This is a second test")
        ('This is a second test', [])
        """
        references = REFERENCE_REGEX.findall(text)
        cleaned_text = REFERENCE_REGEX.sub("", text)

        REFERENCE_ID_REGEX = re.compile(r"\[CQS:([A-Z0-9\-]+)\]")
        # Extract IDs into single list
        extracted_ids = []
        for ref in references:
            match = REFERENCE_ID_REGEX.findall(ref)
            extracted_ids.extend(match)
        return cleaned_text.strip(), extracted_ids

    def extract_bulletpoints_and_references(self) -> list[tuple[str, list[str]]]:
        texts = (
            self.clean_final_report.removeprefix("* ").removesuffix(" \n").split("\n*")
        )
        return [SingleEntityReport._extract_references(t) for t in texts]

    def render(self) -> str:
        entity_str = self.entity_info["name"]
        if "ticker" in self.entity_info and self.entity_info["ticker"]:
            entity_str += f" ({self.entity_info['ticker']})"

        return f"#### {entity_str}\n\n{self.remove_references(self.clean_final_report).replace('$', '&#36;')}"


class TopicMetadata(BaseModel):
    """Represents a topic with its relevance score and source attributions."""

    topic: str = Field(
        description="A topic summarized in concise market intelligence update"
    )
    relevance_score: int = Field(
        description="A relevance score, on a scale of 1 (low) to 5 (high) based on: actionability, materiality, and market impact, one score for each topic"
    )
    source_citation: list[int | str] = Field(
        description="A list of integers where each integer is the Reference ID."
    )


class TopicCollection(BaseModel):
    """Generates a list of topics summarized in concise market intelligence update, each topic comes with the associated relevance score and source attribution reference."""

    collection: list[TopicMetadata] = Field(
        description="A list of topics with their relevance scores and source attributions."
    )


class AnalysisResponse(BaseModel):
    """Generates a list of topics summarized in concise market intelligence update, a list of the novelty contexts and a list of the novelty scores of each topic."""

    topics: list[str] = Field(
        description="A list of topics summarized in concise market intelligence update",
    )
    relevance_score: list[int] = Field(
        description="A list of relevance scores, on a scale of 1 (low) to 5 (high) based on: actionability, materiality, and market impact, one score for each topic",
    )

    @model_validator(mode="after")
    def fix_topics_and_relevance_score_length(self):
        if len(self.relevance_score) != len(self.topics):
            self.relevance_score = [
                settings.INTRO_SECTION_MIN_RELEVANCE_SCORE + 1
            ] * len(self.topics)

        return self


class IntroSection(BaseModel):
    """Generates a string listing bullet points that summarize in a concise list the whole market intelligence update, and a string with a very precise and professional title for the report."""

    intro_section: str = Field(
        description="Provide a quick, punchy briefing that catches attention and captures the key takeaways. 8 bullet points max.",
    )
    report_title: str = Field(
        description="A title that summarizes the most important bullet points in a clear-cut sentence with no fluff or exaggerations.",
    )


class SingleBulletPoint(BaseModel):
    """Generates a single bullet point for a company's most important development."""

    bullet_point: str = Field(
        description="A single bullet point capturing the most important, actionable development for the company.",
    )


class ReportTitle(BaseModel):
    """Generates a report title based on the first bullet point."""

    report_title: str = Field(
        description="A title that summarizes the most important bullet point in a clear-cut sentence with no fluff or exaggerations.",
    )


class WatchlistReport(BaseModel):
    watchlist_id: str
    watchlist_name: str
    report_title: str
    report_date: datetime  # Deprecated
    introduction: str
    entity_reports: list[SingleEntityReport]


class OutputReportBulletPoint(BaseModel):
    """A single bullet point for the output report."""

    bullet_point: str
    sources: list[str]


class OutputEntityReport(BaseModel):
    """A single entity report."""

    entity_id: str
    entity_info: dict
    content: list[OutputReportBulletPoint]


class BriefReport(BaseModel):
    watchlist_id: str
    watchlist_name: str
    is_empty: bool
    start_date: str
    end_date: str
    novelty: bool
    report_title: str
    introduction: str
    entity_reports: list[OutputEntityReport] = []
    source_metadata: ReportedSources

    @classmethod
    def from_watchlist_report(
        cls, watchlist_report: WatchlistReport, sources: RetrievedSources, novelty: bool
    ) -> "BriefReport":
        """Create a BriefReport from a WatchlistReport."""
        # Format entity reports

        entity_reports = []
        for entity_report in watchlist_report.entity_reports:
            content = []
            for text, references in entity_report.extract_bulletpoints_and_references():
                content.append(
                    OutputReportBulletPoint(
                        bullet_point=text,
                        sources=references,
                    )
                )
            entity_reports.append(
                OutputEntityReport(
                    entity_id=entity_report.entity_id,
                    entity_info=entity_report.entity_info,
                    content=content,
                )
            )

        return cls(
            watchlist_id=watchlist_report.watchlist_id,
            watchlist_name=watchlist_report.watchlist_name,
            is_empty=False if watchlist_report.entity_reports else True,
            start_date=watchlist_report.report_date.isoformat(),
            end_date=watchlist_report.report_date.isoformat(),
            novelty=novelty,
            report_title=watchlist_report.report_title,
            introduction=watchlist_report.introduction,
            entity_reports=entity_reports,
            # Convert RetrievedSources to ReportedSources by serializing only used references
            source_metadata=ReportedSources(root=sources.model_dump()),
        )


class PromptConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    system_prompt: str
    user_template: Template
    llm_kwargs: dict


class BulletPointsUsage(BaseModel):
    bullet_points_before_novelty: int = 0
    bullet_points_after_novelty: int = 0
    bullet_points_stored: int = 0

    def __add__(self, other):
        if not isinstance(other, type(self)):
            raise ValueError(
                f"Can't add items that are not BulletPointsUsage: {type(other)}"
            )

        return BulletPointsUsage(
            bullet_points_before_novelty=self.bullet_points_before_novelty
            + other.bullet_points_before_novelty,
            bullet_points_after_novelty=self.bullet_points_after_novelty
            + other.bullet_points_after_novelty,
            bullet_points_stored=self.bullet_points_stored + other.bullet_points_stored,
        )


class LLMUsage(BaseModel):
    model: str = "N/A"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    n_calls: int = 1

    def __add__(self, other):
        if not isinstance(other, type(self)):
            raise ValueError(f"Can't add items that are not LLMUsage: {type(other)}")

        if self.model != other.model:
            raise ValueError(
                f"Can't add items that don't share a model: {self.model=} != {other.model}"
            )

        return LLMUsage(
            model=self.model,
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            n_calls=self.n_calls + other.n_calls,
        )

    def is_empty(self) -> bool:
        """Check if this usage instance has any tokens recorded."""
        return self.total_tokens == 0


class EmbeddingsUsage(BaseModel):
    model: str = "N/A"
    tokens: int = 0

    def __add__(self, other):
        if not isinstance(other, type(self)):
            raise ValueError(
                f"Can't add items that are not EmbeddingsUsage: {type(other)}"
            )

        if self.model != other.model:
            raise ValueError(
                f"Can't add items that don't share a model: {self.model=} != {other.model}"
            )

        return EmbeddingsUsage(
            model=self.model,
            tokens=self.tokens + other.tokens,
        )


class RetrievalTracker(BaseModel):
    retrieval_timestamp: datetime
    entity_id: str | None
    result: list[Result]

    @field_serializer("retrieval_timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()

    @field_validator("retrieval_timestamp", mode="before")
    @classmethod
    def deserialize_timestamp(cls, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            return datetime.fromisoformat(value)
        else:
            raise ValueError(
                "The timestamp field must be a datetime object formatted following ISO-8601."
            )


class TopicContentTracker(BaseModel):
    """Tracks the content of the watchlist report."""

    topic: str
    retrieval: list[RetrievalTracker]

    @property
    def total_documents(self) -> float:
        documents = []
        for retrieval in self.retrieval:
            for result in retrieval.result:
                documents.append(result.document_id)
        return len(set(documents))

    @property
    def total_chunks(self) -> float:
        chunks = 0
        for retrieval in self.retrieval:
            for result in retrieval.result:
                for chunk in result.chunks:
                    chunks += len(result.chunks)
        return chunks

    @property
    def documents_per_topic(self) -> dict[str, int]:
        """Calculates the number of documents per topic."""
        documents_per_topic = {}
        for retrieval in self.retrieval:
            if retrieval.topic is None:
                documents_per_topic["No Topic"] = [
                    c.document_id
                    for r in self.retrieval
                    for c in r.chunks
                    if r.topic is None
                ]
            else:
                documents_per_topic[retrieval.topic] = [
                    c.document_id
                    for r in self.retrieval
                    for c in r.chunks
                    if r.topic == retrieval.topic
                ]

        for topic, documents in documents_per_topic.items():
            documents_per_topic[topic] = len(set(documents))
        return documents_per_topic

    @property
    def chunks_per_topic(self) -> dict[str, int]:
        """Calculates the number of chunks per topic."""
        chunks_per_topic = {}
        for retrieval in self.retrieval:
            if retrieval.topic is None:
                chunks_per_topic["No Topic"] = sum(
                    len(r.chunks) for r in self.retrieval if r.topic is None
                )
            else:
                chunks_per_topic[retrieval.topic] = sum(
                    len(r.chunks) for r in self.retrieval if r.topic == retrieval.topic
                )
        return chunks_per_topic

    def __add__(self, other):
        if not isinstance(other, TopicContentTracker):
            raise TypeError("Unsupported type for addition")
        if self.topic != other.topic:
            raise ValueError("Cannot add content from different topis")

        return TopicContentTracker(
            topic=self.topic,
            retrieval=self.retrieval + other.retrieval,
        )

    @classmethod
    def aggregate_per_topic(
        cls, trackers: list["TopicContentTracker"]
    ) -> dict[str, "TopicContentTracker"]:
        """Aggregates the content per topic."""
        aggregated = {}
        for tracker in trackers:
            if tracker.topic not in aggregated:
                aggregated[tracker.topic] = tracker
            else:
                aggregated[tracker.topic] += tracker
        return aggregated

    @classmethod
    def retrieval_from_sdk_result(
        cls, sdk_results: list[Result], entity_id: str | None = None
    ) -> list[RetrievalTracker]:
        if len(sdk_results) == 0:
            return []
        return [
            RetrievalTracker(
                retrieval_timestamp=datetime.now(),
                entity_id=entity_id,
                result=sdk_results,
            )
        ]
