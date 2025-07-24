from datetime import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from bigdata_briefs.models import (
    ChunkHighlight,
    PipelineOutput,
    ReportDates,
    ReportSources,
    SourceChunkReference,
    WatchlistReport,
)
from bigdata_briefs.sql_models import SQLBriefReport, SQLReportsSources
from bigdata_briefs.storage import write_report_with_sources


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def pipeline_output():
    return PipelineOutput(
        watchlist_id="1",
        is_empty=False,
        report_dates=ReportDates(
            start=datetime(2023, 1, 1), end=datetime(2023, 1, 31), novelty=True
        ),
        watchlist_report=WatchlistReport(
            watchlist_id="1",
            watchlist_name="Test Watchlist",
            report_title="Test Report",
            report_date=datetime(2023, 1, 31),
            introduction="This is a test report.",
            entity_reports=[],
        ),
    )


@pytest.fixture
def source_metadata():
    return ReportSources(
        root={
            "id": SourceChunkReference(
                ref_id=1,
                document_id="doc1",
                headline="Test Headline",
                ts="2023-01-01T00:00:00Z",
                document_scope="full",
                language="en",
                source_key="source1",
                source_name="Test Source",
                source_rank=1,
                url="http://example.com/source1",
                chunk_id=1,
                text="This is a test chunk.",
                highlights=[ChunkHighlight(pnum=1, snum=1)],
            )
        }
    )


def test_write_report_with_sources_db(in_memory_db, pipeline_output, source_metadata):
    write_report_with_sources(pipeline_output, source_metadata, in_memory_db)
    # Check report was written
    with in_memory_db:
        report = in_memory_db.exec(select(SQLBriefReport)).first()
        assert report is not None
        assert report.watchlist_id == pipeline_output.watchlist_id
        # Check sources was written
        sources = in_memory_db.exec(select(SQLReportsSources)).first()
        assert sources is not None
        assert sources.brief_id == report.id


def test_write_report_with_sources_fails_gracefully(capsys, in_memory_db):
    # No exception should be raised
    write_report_with_sources(None, None, in_memory_db)  # ty: ignore[invalid-argument-type]
    capsys.readouterr()  # Capture the logger to avoid cluttering the output
