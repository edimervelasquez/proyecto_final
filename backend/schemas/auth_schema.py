from pydantic import BaseModel, EmailStr
from typing import Optional

# Esquema para /registrar
class UsuarioRegistro(BaseModel):
    empleado: str
    correo: EmailStr
    contrasenia: str
    cedula: str
    id_rol: Optional[int] = 3

# Esquema para /login
class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasenia: str

# Esquema para cambiar estado
class EstadoUpdate(BaseModel):
    estado: str