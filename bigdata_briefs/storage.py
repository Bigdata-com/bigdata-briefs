from sqlmodel import Session

from bigdata_briefs import logger
from bigdata_briefs.models import (
    PipelineOutput,
    ReportSources,
)
from bigdata_briefs.sql_models import SQLBriefReport, SQLReportsSources


def write_report_with_sources(
    pipeline_output: PipelineOutput,
    source_metadata: ReportSources,
    session: Session,
):
    try:
        report = SQLBriefReport(
            watchlist_id=pipeline_output.watchlist_id,
            is_empty=pipeline_output.is_empty,
            report_period_start=pipeline_output.report_dates.start,
            report_period_end=pipeline_output.report_dates.end,
            novelty_enabled=pipeline_output.report_dates.novelty,
            brief_report=pipeline_output.watchlist_report.model_dump_json(),
        )

        sources = SQLReportsSources(
            brief_id=report.id,
            report_sources=source_metadata.model_dump_json(),
        )

        session.add(report)
        session.add(sources)
        session.commit()
        logger.debug(f"Report with ID {report.id} and sources saved successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save report and sources, skipping: {e}")
