from typing import List, Literal, NotRequired, TypedDict


class TimestampFilter(TypedDict):
    start: str
    end: str


class EntityFilter(TypedDict):
    any_of: List[str]


class SentimentRange(TypedDict):
    min: float
    max: float


class SentimentFilter(TypedDict, total=False):
    ranges: List[SentimentRange]
    values: List[Literal["positive", "negative", "neutral"]]  # Deprecated by the API


class SourceFilter(TypedDict):
    mode: Literal["INCLUDE", "EXCLUDE"]
    values: List[str]


class CategoryFilter(TypedDict):
    mode: Literal["INCLUDE", "EXCLUDE"]
    values: List[str]


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
