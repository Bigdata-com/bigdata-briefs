from bigdata_briefs import LOG_LEVEL
from bigdata_briefs.api.app import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level=LOG_LEVEL.lower())
