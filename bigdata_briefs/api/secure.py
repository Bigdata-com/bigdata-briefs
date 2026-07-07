from fastapi import Header, HTTPException, Security
from fastapi.security import APIKeyQuery
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from bigdata_briefs.settings import settings

token_query = APIKeyQuery(name="token", auto_error=False)


async def require_bigdata_api_key(
    x_api_key: str | None = Header(None, alias="X-API-KEY"),
) -> str:
    if not x_api_key or not x_api_key.strip():
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail={
                "error": "API key required",
                "message": (
                    "Please provide your Bigdata API key via the X-API-KEY request header"
                ),
            },
        )
    return x_api_key.strip()


def validate_access_token(token: str | None = Security(token_query)) -> str | None:
    # If no access token is set, do not validate
    if settings.ACCESS_TOKEN is None:
        return None
    # If access token is set, validate it
    if token == settings.ACCESS_TOKEN:
        return token

    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid access token")


query_scheme = validate_access_token
