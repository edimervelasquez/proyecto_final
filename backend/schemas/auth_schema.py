from pydantic import BaseModel, EmailStr, Field
from typing import Literal

# Esquema para /registrar
class UsuarioRegistro(BaseModel):
    empleado: str
    correo: EmailStr
    contrasenia: str
    cedula: str
    id_rol: Literal[2, 3] = 2

# Esquema para /login
class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasenia: str


class EstadoUpdate(BaseModel):
    estado: str = Field(..., min_length=1, max_length=20)


class RolUpdate(BaseModel):
    id_rol: int = Field(..., ge=1)