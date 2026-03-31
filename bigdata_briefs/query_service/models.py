from typing import Literal, NotRequired, TypedDict


class TimestampFilter(TypedDict):
    start: str
    end: str


class EntityFilter(TypedDict):
    any_of: list[str]


class SentimentRangeBand(TypedDict):
    min: float
    max: float


class SentimentFilter(TypedDict, total=False):
    """API supports categorical values or numeric range bands (magnitude filter)."""

    values: list[Literal["positive", "negative", "neutral"]]
    ranges: list[SentimentRangeBand]


class SourceFilter(TypedDict):
    mode: Literal["INCLUDE", "EXCLUDE"]
    values: list[str]


class CategoryFilter(TypedDict):
    mode: Literal["INCLUDE", "EXCLUDE"]
    values: list[str]


class Filters(TypedDict, total=False):
    timestamp: TimestampFilter
    entity: EntityFilter
    sentiment: SentimentFilter
    source: SourceFilter
    category: CategoryFilter


class RerankerParams(TypedDict):
    enabled: bool
    threshold: NotRequired[float]


class RankingParams(TypedDict, total=False):
    source_boost: int
    freshness_boost: int
    reranker: RerankerParams


class SearchAPIQueryDict(TypedDict, total=False):
    auto_enrich_filters: bool
    filters: Filters
    ranking_params: RankingParams
    max_chunks: int
    text: NotRequired[str]
