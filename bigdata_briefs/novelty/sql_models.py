import uuid
from datetime import datetime

from sqlmodel import JSON, Column, Field, SQLModel


class SQLBulletPointEmbedding(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    entity_id: str
    date: datetime
    embedding: list[float] = Field(sa_column=Column(JSON))
    original_text: str
