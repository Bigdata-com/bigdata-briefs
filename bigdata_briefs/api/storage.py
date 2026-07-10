from datetime import datetime
from threading import Lock
from uuid import UUID

from sqlmodel import Session, select

from bigdata_briefs.api.models import BriefStatusResponse, WorkflowStatus
from bigdata_briefs.api.sql_models import SQLWorkflowStatus
from bigdata_briefs.api.utils import status_report_example_models
from bigdata_briefs.sql_models import SQLBriefReport
from bigdata_briefs.storage import get_report_with_sources


class StorageManager:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.lock = Lock()

    def _get_workflow_status(self, request_id: UUID) -> SQLWorkflowStatus | None:
        return self.db_session.exec(
            select(SQLWorkflowStatus).where(SQLWorkflowStatus.id == request_id)
        ).first()

    def _create_workflow_status(
        self, request_id: UUID, status: WorkflowStatus
    ) -> SQLWorkflowStatus:
        return SQLWorkflowStatus(
            id=request_id, status=status, last_updated=datetime.now()
        )

    def update_status(self, request_id: UUID, status: WorkflowStatus):
        with self.lock:
            workflow_status = self._get_workflow_status(request_id)

            if workflow_status is None:
                workflow_status = self._create_workflow_status(request_id, status)
            else:
                workflow_status.status = status
                workflow_status.last_updated = datetime.now()

            self.db_session.add(workflow_status)
            self.db_session.commit()
            self.db_session.refresh(workflow_status)

    def get_status(self, request_id: UUID) -> WorkflowStatus | None:
        with self.lock:
            workflow_status = self._get_workflow_status(request_id)
            if workflow_status is None:
                return None
            return WorkflowStatus(workflow_status.status)

    def log_message(self, request_id: UUID, message: str):
        with self.lock:
            workflow_status = self._get_workflow_status(request_id)
            if workflow_status is None:
                raise ValueError(
                    f"Request ID {request_id} not found in status storage."
                )
            workflow_status.logs.append(message)
            workflow_status.last_updated = datetime.now()
            self.db_session.add(workflow_status)
            self.db_session.commit()
            self.db_session.refresh(workflow_status)

    def get_logs(self, request_id: UUID) -> list[str] | None:
        with self.lock:
            workflow_status = self._get_workflow_status(request_id)
            if workflow_status is None:
                return None
            return workflow_status.logs

    def get_report(self, request_id: UUID) -> BriefStatusResponse | None:
        with self.lock:
            workflow_status = self._get_workflow_status(request_id)
            if workflow_status is None:
                return None
            report = get_report_with_sources(request_id, session=self.db_session)

            return BriefStatusResponse(
                request_id=str(request_id),
                last_updated=workflow_status.last_updated,
                status=WorkflowStatus(workflow_status.status),
                logs=workflow_status.logs,
                report=report,
            )

    def initialize_with_example_data(self):
        """Seed predefined demo briefs (AI Scene, Commodities, Countries).

        Upserts by example ID so refreshed demo content replaces stale rows.
        """

        with self.lock:
            changed = False
            for example_status, example_report in status_report_example_models():
                existing_status = self.db_session.exec(
                    select(SQLWorkflowStatus).where(
                        SQLWorkflowStatus.id == example_status.id
                    )
                ).first()
                existing_report = self.db_session.exec(
                    select(SQLBriefReport).where(SQLBriefReport.id == example_report.id)
                ).first()

                if existing_status is None:
                    self.db_session.add(example_status)
                    changed = True
                else:
                    existing_status.last_updated = example_status.last_updated
                    existing_status.status = example_status.status
                    existing_status.logs = example_status.logs
                    changed = True

                if existing_report is None:
                    self.db_session.add(example_report)
                    changed = True
                else:
                    existing_report.watchlist_id = example_report.watchlist_id
                    existing_report.created_at = example_report.created_at
                    existing_report.is_empty = example_report.is_empty
                    existing_report.report_period_start = example_report.report_period_start
                    existing_report.report_period_end = example_report.report_period_end
                    existing_report.novelty_enabled = example_report.novelty_enabled
                    existing_report.brief_report = example_report.brief_report
                    changed = True

            if changed:
                self.db_session.commit()
