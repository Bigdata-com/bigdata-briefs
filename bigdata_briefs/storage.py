from datetime import datetime

from sqlmodel import Session

from bigdata_briefs import logger
from bigdata_briefs.models import BriefReport
from bigdata_briefs.sql_models import SQLBriefReport, SQLReportsSources


def write_report_with_sources(
    pipeline_output: BriefReport,
    session: Session | None,
):
    if session is None:
        logger.error("No database session provided, skipping report saving.")
        return
    try:
        report = SQLBriefReport(
            watchlist_id=pipeline_output.watchlist_id,
            is_empty=pipeline_output.is_empty,
            report_period_start=datetime.fromisoformat(pipeline_output.start_date),
            report_period_end=datetime.fromisoformat(pipeline_output.end_date),
            brief_report=[
                report.model_dump() for report in pipeline_output.entity_reports
            ],
        )

        sources = SQLReportsSources(
            brief_id=report.id,
            report_sources=pipeline_output.source_metadata.model_dump_json(),
        )

        session.add(report)
        session.add(sources)
        session.commit()
        logger.debug(f"Report with ID {report.id} and sources saved successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save report and sources, skipping: {e}")
