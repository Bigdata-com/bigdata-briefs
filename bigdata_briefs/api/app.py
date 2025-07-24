import time
from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi.responses import HTMLResponse
from sqlmodel import Session, SQLModel, create_engine

from bigdata_briefs import LOG_LEVEL, __version__, logger
from bigdata_briefs.api.models import BriefCreationRequest
from bigdata_briefs.metrics import (
    LLMMetrics,
    Metrics,
)
from bigdata_briefs.novelty.storage import SQLiteEmbeddingStorage
from bigdata_briefs.query_service.query_service import (
    QueryService,
)
from bigdata_briefs.service import BriefPipelineService
from bigdata_briefs.settings import settings
from bigdata_briefs.templates import loader

engine = create_engine(settings.DB_STRING, echo=LOG_LEVEL == "DEBUG")

embedding_storage = SQLiteEmbeddingStorage(engine)
query_service = QueryService()
brief_service = BriefPipelineService.factory(
    query_service, embedding_storage=embedding_storage
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    yield


def get_session():
    with Session(engine) as session:
        yield session


def lifespan(app: FastAPI):
    query_service.send_trace(
        event_name=query_service.TraceEventName.SERVICE_START,
        trace={
            "version": __version__,
        },
    )
    create_db_and_tables()
    yield


app = FastAPI(
    title="Briefs service by Bigdata.com",
    description="API for generating timely briefs based on data from Bigdata.com",
    version=__version__,
    lifespan=lifespan,
)


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


@app.get("/")
async def sample_frontend():
    # Create an instance of BriefCreationRequest to get default values
    default_request = BriefCreationRequest()

    return HTMLResponse(
        content=loader.get_template("api/frontend.html.jinja").render(
            watchlist_id=default_request.watchlist_id,
            novelty=default_request.novelty,
            default_start_date=default_request.report_start_date.strftime("%Y-%m-%d"),
            default_end_date=default_request.report_end_date.strftime("%Y-%m-%d"),
        )
    )


@app.get("/briefs/create")
async def create_brief(
    brief_config: Annotated[BriefCreationRequest, Query()],
    session: Session = Depends(get_session),
):
    """
    Endpoint to create a brief.
    This is a placeholder for the actual implementation.
    """
    [cls.reset_usage() for cls in Metrics.__subclasses__()]
    LLMMetrics.reset_usage()
    response = brief_service.generate_brief(
        brief_config,
        db_session=session,
    )

    return response
