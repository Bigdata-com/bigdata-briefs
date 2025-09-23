import uuid
from datetime import datetime

from sqlmodel import Session, select

from bigdata_briefs import logger
from bigdata_briefs.models import BriefReport
from bigdata_briefs.sql_models import SQLBriefReport


def write_report_with_sources(
    request_id: str,
    pipeline_output: BriefReport,
    session: Session | None,
):
    if session is None:
        logger.error("No database session provided, skipping report saving.")
        return
    try:
        report = SQLBriefReport(
            id=uuid.UUID(request_id),
            watchlist_id=pipeline_output.watchlist_id,
            is_empty=pipeline_output.is_empty,
            report_period_start=datetime.fromisoformat(pipeline_output.start_date),
            report_period_end=datetime.fromisoformat(pipeline_output.end_date),
            novelty_enabled=pipeline_output.novelty,
            brief_report=pipeline_output.model_dump_json(),
        )

        session.add(report)
        session.commit()
        logger.debug(f"Report with ID {report.id} and sources saved successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save report and sources, skipping: {e}")


def get_report_with_sources(
    request_id: str,
    session: Session | None,
) -> BriefReport | None:
    if session is None:
        logger.error("No database session provided, cannot fetch report.")
        return None

    report = session.exec(
        select(SQLBriefReport).where(SQLBriefReport.id == uuid.UUID(request_id))
    ).first()
    if report is None:
        return None

    try:
        brief_report = BriefReport.model_validate_json(report.brief_report)
        return brief_report
    except Exception as e:
        logger.error(f"Error reconstructing BriefReport from database records: {e}")
        return None
