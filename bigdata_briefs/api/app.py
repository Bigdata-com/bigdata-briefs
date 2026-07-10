import time
from functools import partial
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, Body, Depends, FastAPI, HTTPException, Security
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel, create_engine

from bigdata_briefs import LOG_LEVEL, __version__, logger
from bigdata_briefs.api.examples import EXAMPLE_UUID
from bigdata_briefs.api.examples_demo import (
    COMMODITIES_EXAMPLE_UUID,
    COUNTRIES_EXAMPLE_UUID,
)
from bigdata_briefs.api.models import (
    BriefAcceptedResponse,
    BriefCreationRequest,
    BriefStatusResponse,
    ExampleWatchlists,
    WorkflowStatus,
)
from bigdata_briefs.api.secure import query_scheme, require_bigdata_api_key
from bigdata_briefs.api.storage import StorageManager
from bigdata_briefs.api.utils import get_example_values_from_schema
from bigdata_briefs.metrics import (
    LLMMetrics,
    Metrics,
)
from bigdata_briefs.novelty.storage import SQLiteEmbeddingStorage
from bigdata_briefs.query_service.api import APIQueryService
from bigdata_briefs.service import BriefPipelineService
from bigdata_briefs.settings import settings
from bigdata_briefs.templates import loader
from bigdata_briefs.tracing.service import TracingService

engine = create_engine(settings.DB_STRING, echo=LOG_LEVEL == "DEBUG")

embedding_storage = SQLiteEmbeddingStorage(engine)


def build_pipeline_services(api_key: str) -> tuple[BriefPipelineService, APIQueryService]:
    query_service = APIQueryService(api_key=api_key)
    brief_service = BriefPipelineService.factory(
        query_service=query_service,
        tracing_service=TracingService(api_key=api_key),
        embedding_storage=embedding_storage,
    )
    return brief_service, query_service


def run_brief_generation(
    api_key: str,
    brief_config: BriefCreationRequest,
    request_id: UUID,
    storage_manager: StorageManager,
) -> None:
    brief_service, query_service = build_pipeline_services(api_key)
    try:
        brief_service.generate_brief(
            brief_config,
            request_id=request_id,
            storage_manager=storage_manager,
        )
    finally:
        query_service.cleanup()


def create_db_and_tables():
    logger.info("Setting up data storage", db_string=settings.DB_STRING)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def get_storage_manager(session: Session = Depends(get_session)) -> StorageManager:
    return StorageManager(session)


def lifespan(app: FastAPI):
    logger.info("Starting Bigdata briefs service", version=__version__)
    create_db_and_tables()

    # Initialize the database with example data
    with Session(engine) as session:
        storage_manager = StorageManager(session)
        storage_manager.initialize_with_example_data()

    yield


app = FastAPI(
    title="Briefs service by Bigdata.com",
    description="API for generating timely briefs based on data from Bigdata.com",
    version=__version__,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")


@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    logger.info(
        f"Request completed in {duration:.3f} seconds",
        method=request.method,
        path=str(request.url.path),
        duration=round(duration, 3),
        status_code=response.status_code,
    )
    return response


@app.get(
    "/health",
    summary="Health check endpoint",
)
def health_check():
    return {"status": "ok", "version": __version__}


@app.get(
    "/api/config",
    summary="Public config for the web UI (API key gate).",
)
def api_config():
    return {"bigdata_api_key_configured": False}


@app.get(
    "/",
    summary="Web UI for creating and viewing briefs (demo).",
    response_class=HTMLResponse,
)
async def sample_frontend(_: str = Security(query_scheme)):
    example_values = get_example_values_from_schema(BriefCreationRequest)
    return HTMLResponse(
        content=loader.get_template("api/index.html.jinja").render(
            companies=example_values["entities"],
            novelty=example_values["novelty"],
            default_start_date=example_values["report_start_date"].isoformat(),
            default_end_date=example_values["report_end_date"].isoformat(),
            topics=example_values["topics"],
            sources=example_values["sources"],
            example_watchlists=list(dict(ExampleWatchlists).values()),
            example_request_id=str(EXAMPLE_UUID),
            demo_examples=[
                {
                    "id": "ai-scene",
                    "label": "AI Scene",
                    "description": "Tech & AI leaders",
                    "period": "2026-07-02 → 2026-07-09",
                    "request_id": str(EXAMPLE_UUID),
                },
                {
                    "id": "commodities",
                    "label": "Commodities",
                    "description": "Oil, gold, copper, gas",
                    "period": "2026-07-02 → 2026-07-09",
                    "request_id": str(COMMODITIES_EXAMPLE_UUID),
                },
                {
                    "id": "countries",
                    "label": "Countries",
                    "description": "US, China, Germany, Japan, India",
                    "period": "2026-07-02 → 2026-07-09",
                    "request_id": str(COUNTRIES_EXAMPLE_UUID),
                },
            ],
            demo_mode=settings.DEMO_MODE,
        ),
        media_type="text/html",
    )


@app.post(
    "/briefs/create",
    summary="Create a brief based on the provided configuration.",
    response_model=BriefAcceptedResponse,
)
async def create_brief(
    brief_config: Annotated[BriefCreationRequest, Body()],
    background_tasks: BackgroundTasks,
    storage_manager: StorageManager = Depends(get_storage_manager),
    api_key: str = Depends(require_bigdata_api_key),
    _: str = Security(query_scheme),
) -> JSONResponse:
    """
    Endpoint to create a brief.
    This is a placeholder for the actual implementation.
    """
    [cls.reset_usage() for cls in Metrics.__subclasses__()]
    LLMMetrics.reset_usage()

    request_id = uuid4()
    storage_manager.update_status(request_id, WorkflowStatus.QUEUED)

    background_tasks.add_task(
        partial(
            run_brief_generation,
            api_key,
            brief_config,
            request_id,
            storage_manager,
        )
    )

    return JSONResponse(
        status_code=202,
        content=BriefAcceptedResponse(
            request_id=str(request_id), status=WorkflowStatus.QUEUED
        ).model_dump(),
    )


@app.get(
    "/briefs/status/{request_id}",
    summary="Get the status of a brief report",
)
def get_status(
    request_id: UUID,
    storage_manager: StorageManager = Depends(get_storage_manager),
    _api_key: str = Depends(require_bigdata_api_key),
    _: str = Security(query_scheme),
) -> BriefStatusResponse:
    """Get the status of a brief report by its request_id. If the report is still running,
    you will get the current status and logs. If the report is completed, you will also get the
    complete report"""
    report = storage_manager.get_report(request_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Request ID not found")
    return report
