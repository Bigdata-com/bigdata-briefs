import time
from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi.responses import HTMLResponse
from sqlmodel import Session, SQLModel, create_engine

from bigdata_briefs import __version__, logger
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

engine = create_engine(settings.DB_STRING, echo=True)

embedding_storage = SQLiteEmbeddingStorage(engine)
query_service = QueryService()
brief_service = BriefPipelineService.factory(
    query_service, embedding_storage=embedding_storage
)


def create_db_and_tables(app: FastAPI):
    logger.debug
    SQLModel.metadata.create_all(engine)
    yield


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI(
    title="Briefs service by Bigdata.com",
    description="API for generating timely briefs based on data from Bigdata.com",
    version=__version__,
    lifespan=create_db_and_tables,
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
    return HTMLResponse(
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Watchlist Briefs</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 2em;
      background: #f5f5f5;
      color: #333;
    }
    input[type="text"],
    input[type="date"],
    select {
      width: 300px;
      padding: 8px;
      font-size: 16px;
      margin-bottom: 10px;
      display: block;
    }
    button {
      padding: 8px 12px;
      font-size: 16px;
      cursor: pointer;
    }
    pre {
      background-color: #272822;
      color: #f8f8f2;
      padding: 16px;
      white-space: pre-wrap;
      word-wrap: break-word;
      overflow: auto;
      border-radius: 5px;
      margin-top: 20px;
    }
    .error {
      color: red;
    }
  </style>
</head>
<body>
  <h1>Get Brief for Watchlist</h1>

  <label for="watchlist_id">Watchlist ID:</label>
  <input type="text" id="watchlist_id" placeholder="Enter watchlist ID" value="672c2d70-2062-4330-a0a7-54c598f231db" />

  <label for="report_start_date">Report Start Date:</label>
  <input type="date" id="report_start_date" value="2024-01-01" />

  <label for="report_end_date">Report End Date:</label>
  <input type="date" id="report_end_date" value="2024-01-31" />

  <label for="novelty">Novelty:</label>
  <select id="novelty">
    <option value="true" selected>true</option>
    <option value="false">false</option>
  </select>

  <button onclick="fetchBrief()">Generate Brief</button>
  <div id="spinner" style="display:none;">⏳ Loading...</div>
  <pre id="output"></pre>

  <script>
    async function fetchBrief() {
        const watchlistId = document.getElementById('watchlist_id').value.trim();
        const startDate = document.getElementById('report_start_date').value;
        const endDate = document.getElementById('report_end_date').value;
        const novelty = document.getElementById('novelty').value;
        const output = document.getElementById('output');
        const spinner = document.getElementById('spinner');

        output.textContent = '';
        output.classList.remove('error');

        if (!watchlistId) {
            output.textContent = '❌ Please enter a watchlist ID.';
            output.classList.add('error');
            return;
        }

        // Show spinner while fetching
        spinner.style.display = 'block';

        const url = `/briefs/create?watchlist_id=${encodeURIComponent(watchlistId)}&report_start_date=${encodeURIComponent(startDate)}&report_end_date=${encodeURIComponent(endDate)}&novelty=${encodeURIComponent(novelty)}`;

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }

            const data = await response.json();
            output.textContent = JSON.stringify(data, null, 2);
        } catch (err) {
            output.textContent = `❌ Error: ${err.message}`;
            output.classList.add('error');
        } finally {
            // Hide spinner after fetching
            spinner.style.display = 'none';
        }
    }
  </script>
</body>
</html>"""
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
