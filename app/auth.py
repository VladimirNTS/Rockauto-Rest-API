from fastapi import Request, HTTPException, Security, status, Depends
import secrets
from fastapi.security.api_key import APIKeyQuery, APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from app.config import PARTS_SOFT_API_KEYS


api_key_query = APIKeyQuery(name="API key", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

print(PARTS_SOFT_API_KEYS)

async def get_api_key(
    api_key_q: str = Security(api_key_query),
    api_key_h: str = Security(api_key_header),
):
    api_key = api_key_q or api_key_h
    if not api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="API key required",
        )

    for valid_key in PARTS_SOFT_API_KEYS:
        if secrets.compare_digest(api_key, valid_key):
            return PARTS_SOFT_API_KEYS[valid_key]

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Invalid API key",
    )

    
