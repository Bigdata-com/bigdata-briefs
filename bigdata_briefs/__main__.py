from bigdata_briefs import LOG_LEVEL
from bigdata_briefs.api.app import app
from bigdata_briefs.settings import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=settings.HOST, port=settings.PORT, log_level=LOG_LEVEL.lower()
    )
