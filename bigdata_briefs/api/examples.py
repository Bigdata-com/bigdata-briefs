from typing import Final
from uuid import UUID

from bigdata_briefs.api.example_loader import build_example_models
from bigdata_briefs.api.sql_models import SQLWorkflowStatus
from bigdata_briefs.sql_models import SQLBriefReport

EXAMPLE_UUID: Final[UUID] = UUID("11111111-1111-1111-1111-111111111112")
AI_SCENE_EXAMPLE_FILE: Final[str] = "example_ai_scene.json"

EXAMPLE_STATUS: Final[SQLWorkflowStatus]
EXAMPLE_REPORT: Final[SQLBriefReport]
EXAMPLE_STATUS, EXAMPLE_REPORT = build_example_models(
    EXAMPLE_UUID, AI_SCENE_EXAMPLE_FILE
)
