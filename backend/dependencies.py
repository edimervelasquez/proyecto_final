from typing import Any

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


bearer_scheme = HTTPBearer()


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    token_payload = getattr(request.state, "token_payload", None)
    if token_payload is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Token requerido.")
    return token_payload
