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
