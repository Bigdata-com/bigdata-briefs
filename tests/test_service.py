from unittest.mock import MagicMock

import pytest
from bigdata_client.models.entities import Company

from bigdata_briefs.models import (
    Chunk,
    ChunkHighlight,
    Entity,
    FollowUpAnalysis,
    QAPairs,
    QuestionAnswer,
    ReportDates,
    Result,
    TopicCollection,
    TopicMetadata,
)
from bigdata_briefs.service import BriefPipelineService


@pytest.fixture
def mock_service():
    llm_client = MagicMock()
    query_service = MagicMock()
    novelty_filter_service = MagicMock()
    service = BriefPipelineService(
        llm_client=llm_client,
        query_service=query_service,
        novelty_filter_service=novelty_filter_service,
    )
    return service, llm_client, query_service, novelty_filter_service


@pytest.fixture
def mock_entity():
    entity = Entity(id="test", name="Test Entity", entity_type="COMP")
    entity._raw = Company(
        id="test_id",
        name="Test Company",
    )
    return entity


@pytest.fixture
def mock_report_dates():
    return ReportDates(start="2023-01-01", end="2023-01-31", novelty=True)


@pytest.fixture
def mock_results():
    return [
        Result(
            document_id="doc1",
            headline="Test Document 1",
            timestamp="2023-01-15T00:00:00Z",
            source_key="source1",
            source_name="Source 1",
            ts="2023-01-15T00:00:00Z",
            document_scope="Empty",
            language="en",
            chunks=[
                Chunk(
                    text="This is a test chunk from document 1.",
                    chunk=1,
                    relevance=0.9,
                    sentiment=0.9,
                    highlights=[
                        ChunkHighlight(
                            pnum=1,
                            snum=1,
                        )
                    ],
                )
            ],
        ),
        Result(
            document_id="doc2",
            headline="Test Document 2",
            timestamp="2023-01-20T00:00:00Z",
            source_key="source2",
            source_name="Source 2",
            ts="2023-01-20T00:00:00Z",
            document_scope="Empty",
            language="en",
            chunks=[
                Chunk(
                    text="This is a test chunk from document 2.",
                    chunk=1,
                    relevance=0.8,
                    sentiment=0.8,
                    highlights=[
                        ChunkHighlight(
                            pnum=1,
                            snum=1,
                        )
                    ],
                )
            ],
        ),
    ]


@pytest.fixture
def mock_qa_pairs(mock_results):
    return QAPairs(
        pairs=[
            QuestionAnswer(
                question="What is the impact of the test?",
                answer=mock_results,
            )
        ]
    )


def test_generate_follow_up_questions(
    mock_service, mock_entity, mock_report_dates, mock_results
):
    service, llm_client, _, _ = mock_service
    # Mock the LLM client response
    llm_client.call_with_response_format.return_value = FollowUpAnalysis(
        questions=["Q1", "Q2"]
    )

    questions = service.generate_follow_up_questions(
        mock_entity, mock_report_dates, mock_results
    )
    assert questions == ["Q1", "Q2"]
    llm_client.call_with_response_format.assert_called()


def test_generate_new_report(
    mock_service, mock_entity, mock_report_dates, mock_qa_pairs
):
    service, llm_client, _, _ = mock_service
    # Mock the LLM client response
    llm_client.call_with_response_format.return_value = TopicCollection(
        collection=[
            TopicMetadata(
                topic="topic1",
                relevance_score=3,
                source_citation=[1],
            )
        ]
    )
    report, sources = service.generate_new_report(
        mock_entity, mock_qa_pairs, mock_report_dates
    )
    # Assertions
    assert report.entity_id == mock_entity.id
    assert report.report_bulletpoints == ["topic1`:ref[LIST:[CQS:doc1-1]]`"]
    assert report.relevance_score == [3]
    assert len(sources.root) == 2
    llm_client.call_with_response_format.assert_called()


def test_create_no_info_report(mock_service, mock_entity):
    service, _, _, _ = mock_service
    message = "No info available"
    generation_step = "TEST_STEP"
    report, sources = service.create_no_info_report(
        mock_entity, message, generation_step
    )
    assert report.entity_id == mock_entity.id
    assert report.report_bulletpoints == [message]
    assert report.relevance_score == [1]
    assert report.clean_final_report == ""
    assert report.is_no_info_report
    assert sources == {}
    assert (mock_entity, generation_step) in service.no_info_reports
