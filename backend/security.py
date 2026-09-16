import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict

from backend.config import Config


TOKEN_TTL_SECONDS = 60 * 60


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _secret() -> bytes:
    return (os.environ.get("SECRET_KEY") or Config.SECRET_KEY).encode("utf-8")


def create_access_token(user_id: int, role: str) -> str:
    header = _encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode("utf-8"))
    payload = _encode(
        json.dumps(
            {
                "sub": str(user_id),
                "role": role,
                "exp": int(time.time()) + TOKEN_TTL_SECONDS,
            }
        ).encode("utf-8")
    )
    content = f"{header}.{payload}".encode("ascii")
    signature = _encode(hmac.new(_secret(), content, hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def validate_access_token(token: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Token con formato inválido.")

    content = f"{parts[0]}.{parts[1]}".encode("ascii")
    expected_signature = _encode(
        hmac.new(_secret(), content, hashlib.sha256).digest()
    )
    if not hmac.compare_digest(parts[2], expected_signature):
        raise ValueError("Token inválido.")

    try:
        payload = json.loads(_decode(parts[1]).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Contenido del token inválido.") from exc

    if not isinstance(payload, dict) or not payload.get("sub"):
        raise ValueError("Token sin usuario.")
    if not isinstance(payload.get("exp"), int) or payload["exp"] <= int(time.time()):
        raise ValueError("Token expirado.")

    return payload
