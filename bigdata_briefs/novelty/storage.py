from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from bigdata_briefs.novelty.models import BulletPointEmbedding
from bigdata_briefs.novelty.sql_models import SQLBulletPointEmbedding


class EmbeddingStorage(ABC):
    @abstractmethod
    def retrieve(
        self, entity_id: str, *, start_date: datetime, end_date: datetime
    ) -> list[BulletPointEmbedding]: ...

    @abstractmethod
    def store(self, data: list[BulletPointEmbedding]): ...


class SQLiteEmbeddingStorage(EmbeddingStorage):
    def __init__(self, engine: Engine):
        self.engine = engine

    def retrieve(
        self, entity_id: str, start_date: datetime, end_date: datetime
    ) -> list[BulletPointEmbedding]:
        with Session(self.engine) as session:
            results = session.exec(
                select(SQLBulletPointEmbedding).where(
                    SQLBulletPointEmbedding.entity_id == entity_id,
                    SQLBulletPointEmbedding.date >= start_date,
                    SQLBulletPointEmbedding.date <= end_date,
                )
            ).all()
            return [
                BulletPointEmbedding(
                    date=r.date,
                    entity_id=entity_id,
                    embedding=r.embedding,
                    original_text=r.original_text,
                )
                for r in results
            ]

    def store(self, data: list[BulletPointEmbedding]):
        with Session(self.engine) as session:
            for bp_embedding in data:
                sql_embedding = SQLBulletPointEmbedding(
                    entity_id=bp_embedding.entity_id,
                    date=bp_embedding.date,
                    embedding=bp_embedding.embedding,
                    original_text=bp_embedding.original_text,
                )
                session.add(sql_embedding)
            session.commit()
