import uuid
from datetime import datetime
from threading import Lock

from sqlmodel import Session, select

from bigdata_briefs.api.models import BriefStatusResponse, WorkflowStatus
from bigdata_briefs.api.sql_models import SQLWorkflowStatus
from bigdata_briefs.storage import get_report_with_sources


class StorageManager:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.lock = Lock()

    def _get_workflow_status(self, request_id: str) -> SQLWorkflowStatus | None:
        return self.db_session.exec(
            select(SQLWorkflowStatus).where(
                SQLWorkflowStatus.id == uuid.UUID(request_id)
            )
        ).first()

    def _create_workflow_status(
        self, request_id: str, status: WorkflowStatus
    ) -> SQLWorkflowStatus:
        return SQLWorkflowStatus(
            id=uuid.UUID(request_id), status=status, last_updated=datetime.now()
        )

    def update_status(self, request_id: str, status: WorkflowStatus):
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

    def get_status(self, request_id: str) -> WorkflowStatus | None:
        with self.lock:
            workflow_status = self._get_workflow_status(request_id)
            if workflow_status is None:
                return None
            return workflow_status.status

    def log_message(self, request_id: str, message: str):
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

    def get_logs(self, request_id: str) -> list[str] | None:
        with self.lock:
            workflow_status = self._get_workflow_status(request_id)
            if workflow_status is None:
                return None
            return workflow_status.logs

    def get_report(self, request_id: str) -> BriefStatusResponse | None:
        with self.lock:
            workflow_status = self._get_workflow_status(request_id)
            if workflow_status is None:
                return None
            report = get_report_with_sources(request_id, session=self.db_session)

            return BriefStatusResponse(
                request_id=request_id,
                last_updated=workflow_status.last_updated,
                status=workflow_status.status,
                logs=workflow_status.logs,
                report=report,
            )
