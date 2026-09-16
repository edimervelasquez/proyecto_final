from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.auth_schema import UsuarioLogin, UsuarioRegistro
from backend.controllers.auth_controller import AuthController

router = APIRouter()

# Esquema para recibir el estado en formato JSON desde el frontend
class EstadoUpdate(BaseModel):
    estado: str

@router.post("/login")
def login(data: UsuarioLogin, db: Session = Depends(get_db)):
    return AuthController.login(data, db)

@router.post("/registrar", status_code=status.HTTP_201_CREATED)
def registrar(data: UsuarioRegistro, db: Session = Depends(get_db)):
    return AuthController.registrar(data, db)

@router.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    return AuthController.listar_usuarios(db)

@router.put("/usuarios/{user_id}/estado")
def actualizar_estado(user_id: int, body: EstadoUpdate, db: Session = Depends(get_db)):
    return AuthController.cambiar_estado(user_id, body.estado, db)

@router.delete("/usuarios/{user_id}")
def eliminar_usuario(user_id: int, db: Session = Depends(get_db)):
    return AuthController.eliminar_usuario(user_id, db)