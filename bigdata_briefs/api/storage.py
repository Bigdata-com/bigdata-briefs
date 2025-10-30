from datetime import datetime
from threading import Lock
from uuid import UUID

from sqlmodel import Session, select

from bigdata_briefs.api.models import BriefStatusResponse, WorkflowStatus
from bigdata_briefs.api.sql_models import SQLWorkflowStatus
from bigdata_briefs.api.utils import status_report_example_models
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
        """Initialize the database with example data for testing and demonstration purposes.
        This method adds a predefined workflow status and report to the database.
        Only works if the database is empty.
        """

        with self.lock:
            example_status, example_report = status_report_example_models()
            # Check if the example id already exists in the database
            existing_id = self.db_session.exec(
                select(SQLWorkflowStatus).where(
                    SQLWorkflowStatus.id == example_status.id
                )
            ).first()
            if existing_id is not None:
                return  # Database already initialized with example data

            self.db_session.add(example_status)
            self.db_session.add(example_report)
            self.db_session.commit()
