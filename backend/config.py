import os
import secrets
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_ENVIRONMENT = {
    "SECRET_KEY": lambda: secrets.token_urlsafe(48),
    "INITIAL_ADMIN_TOKEN": lambda: secrets.token_urlsafe(48),
    "APP_ENV": lambda: "production",
    "PASSWORD_MIN_LENGTH": lambda: "12",
    "DATABASE_URL": lambda: (
        "mysql+pymysql://root:123456@localhost/yullita_creaciones"
    ),
    "HOST": lambda: "127.0.0.1",
    "PORT": lambda: "8000",
    "SMTP_HOST": lambda: "smtp.gmail.com",
    "SMTP_PORT": lambda: "587",
    "SMTP_USERNAME": lambda: "",
    "SMTP_PASSWORD": lambda: "",
    "SMTP_FROM_EMAIL": lambda: "",
    "SMTP_USE_TLS": lambda: "true",
    "SMTP_USE_SSL": lambda: "false",
    "CORS_ALLOWED_ORIGINS": lambda: (
        "http://localhost:5173,http://127.0.0.1:5173"
    ),
    "VITE_API_URL": lambda: "http://127.0.0.1:8000/api",
}


def _read_env_file(env_file: Path, environment: dict[str, str]) -> None:
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and not environment.get(key, "").strip():
            environment[key] = value


def initialize_environment(
    env_file: Path = ENV_FILE,
    environment: dict[str, str] | None = None,
) -> None:
    target_environment = os.environ if environment is None else environment
    _read_env_file(env_file, target_environment)

    missing = {}
    for key, factory in DEFAULT_ENVIRONMENT.items():
        if key not in target_environment:
            missing[key] = factory()
        elif not target_environment[key]:
            default_value = factory()
            if default_value:
                missing[key] = default_value
    if not missing:
        return

    try:
        with env_file.open("a", encoding="utf-8") as file:
            if env_file.stat().st_size:
                file.write("\n")
            for key, value in missing.items():
                file.write(f"{key}={value}\n")
                target_environment[key] = value
    except OSError as exc:
        raise RuntimeError(
            f"No se pudo crear o actualizar el archivo de configuración {env_file}."
        ) from exc


initialize_environment()


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    APP_ENV = os.environ.get("APP_ENV", "production").strip().lower()
    try:
        PASSWORD_MIN_LENGTH = int(os.environ.get("PASSWORD_MIN_LENGTH", "12"))
    except ValueError as exc:
        raise RuntimeError("PASSWORD_MIN_LENGTH debe ser un número entero.") from exc
    if not 4 <= PASSWORD_MIN_LENGTH <= 128:
        raise RuntimeError("PASSWORD_MIN_LENGTH debe estar entre 4 y 128.")
    if APP_ENV != "development" and PASSWORD_MIN_LENGTH < 12:
        raise RuntimeError(
            "PASSWORD_MIN_LENGTH no puede ser menor de 12 fuera de desarrollo."
        )
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HOST = os.environ["HOST"]
    try:
        PORT = int(os.environ["PORT"])
    except ValueError as exc:
        raise RuntimeError("PORT debe ser un número entero.") from exc
    if not 1 <= PORT <= 65535:
        raise RuntimeError("PORT debe estar entre 1 y 65535.")
