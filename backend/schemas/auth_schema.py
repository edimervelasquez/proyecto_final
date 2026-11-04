from pydantic import BaseModel, EmailStr, Field
from typing import Literal

from backend.config import Config

# Esquema para /registrar
class UsuarioRegistro(BaseModel):
    empleado: str = Field(..., min_length=1, max_length=100)
    correo: EmailStr
    contrasenia: str = Field(
        ...,
        min_length=Config.PASSWORD_MIN_LENGTH,
        max_length=128,
        description=(
            "Mínimo de caracteres configurado para el entorno "
            f"{Config.APP_ENV} ({Config.PASSWORD_MIN_LENGTH})."
        ),
    )
    cedula: str = Field(..., min_length=1, max_length=20)
    id_rol: Literal[2, 3] = 2


class UsuarioAdminBootstrap(BaseModel):
    empleado: str = Field(..., min_length=1, max_length=100)
    correo: EmailStr
    contrasenia: str = Field(
        ...,
        min_length=Config.PASSWORD_MIN_LENGTH,
        max_length=128,
        description=(
            "Mínimo de caracteres configurado para el entorno "
            f"{Config.APP_ENV} ({Config.PASSWORD_MIN_LENGTH})."
        ),
    )
    cedula: str = Field(..., min_length=1, max_length=20)


# Esquema para /login
class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasenia: str = Field(..., max_length=128)


class EstadoUpdate(BaseModel):
    estado: Literal["PENDIENTE", "APROBADO", "ACTIVO", "INACTIVO"]


class RolUpdate(BaseModel):
    id_rol: int = Field(..., ge=1)