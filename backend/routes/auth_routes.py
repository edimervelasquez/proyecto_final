from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from backend.controllers.auth_controller import AuthController
from backend.database import get_db
from backend.schemas.auth_schema import (
    EstadoUpdate,
    RolUpdate,
    UsuarioAdminBootstrap,
    UsuarioLogin,
    UsuarioRegistro,
)
from backend.services.auth_service import AuthService

router = APIRouter()

@router.post("/login")
def login(data: UsuarioLogin, db: Session = Depends(get_db)):
    return AuthController.login(data, db)

@router.post("/registrar", status_code=status.HTTP_201_CREATED)
def registrar(data: UsuarioRegistro, db: Session = Depends(get_db)):
    return AuthController.registrar(data, db)


@router.post("/bootstrap-admin", status_code=status.HTTP_201_CREATED)
def bootstrap_admin(
    data: UsuarioAdminBootstrap,
    db: Session = Depends(get_db),
    initial_admin_token: str | None = Header(
        default=None,
        alias="X-Initial-Admin-Token",
    ),
):
    return AuthService.bootstrap_admin_service(data, initial_admin_token, db)


@router.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    return AuthController.listar_usuarios(db)

@router.put("/usuarios/{user_id}/estado")
def actualizar_estado(user_id: int, body: EstadoUpdate, db: Session = Depends(get_db)):
    return AuthController.cambiar_estado(user_id, body, db)

@router.put("/usuarios/{user_id}/rol")
def actualizar_rol(user_id: int, body: RolUpdate, db: Session = Depends(get_db)):
    return AuthController.cambiar_rol(user_id, body, db)

@router.delete("/usuarios/{user_id}")
def eliminar_usuario(user_id: int, db: Session = Depends(get_db)):
    return AuthController.eliminar_usuario(user_id, db)