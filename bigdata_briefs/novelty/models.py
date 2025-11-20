from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BulletPointEmbedding(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    date: datetime
    entity_id: str
    embedding: list[float]
    original_text: str
    _is_novel: bool = True

    def is_novel(self):
        return self._is_novel

    def set_novel(self, value: bool):
        self._is_novel = value


class DiscardedBulletPoint(BaseModel):
    """Represents a bullet point that was discarded during novelty filtering."""
    text: str
    max_similarity: float
    most_similar_text: str


class NoveltyDebugInfo(BaseModel):
    """Debug information about the novelty filtering process for a single entity."""
    entity_id: str
    entity_name: str
    generated_texts: list[str]
    compared_with: list[str]
    discarded: list[DiscardedBulletPoint]
    kept_texts: list[str]
