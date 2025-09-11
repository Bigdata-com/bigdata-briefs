from fastapi import HTTPException, Security
from fastapi.security import APIKeyQuery
from starlette.status import HTTP_403_FORBIDDEN

from bigdata_briefs.settings import settings

token_query = APIKeyQuery(name="token", auto_error=False)


def validate_access_token(token: str | None = Security(token_query)) -> str | None:
    # If no access token is set, do not validate
    if settings.ACCESS_TOKEN is None:
        return None
    # If access token is set, validate it
    if token == settings.ACCESS_TOKEN:
        return token

    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid access token")


query_scheme = validate_access_token
