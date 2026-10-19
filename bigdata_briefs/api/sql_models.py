import uuid

from pydantic import NaiveDatetime
from sqlalchemy.ext.mutable import MutableList
from sqlmodel import JSON, Column, Field, SQLModel


class SQLWorkflowStatus(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True)
    last_updated: NaiveDatetime
    status: str
    logs: list[str] = Field(
        default_factory=list, sa_column=Column(MutableList.as_mutable(JSON))
    )
