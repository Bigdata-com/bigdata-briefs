from typing import List, Literal, NotRequired, TypedDict


class TimestampFilter(TypedDict):
    start: str
    end: str


class EntityFilter(TypedDict):
    any_of: List[str]


class SentimentFilter(TypedDict):
    values: List[Literal["positive", "negative", "neutral"]]


class SourceFilter(TypedDict):
    mode: Literal["INCLUDE", "EXCLUDE"]
    values: List[str]


class Filters(TypedDict, total=False):
    timestamp: TimestampFilter
    entity: EntityFilter
    sentiment: SentimentFilter
    source: SourceFilter


class RerankerParams(TypedDict):
    enabled: bool


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
