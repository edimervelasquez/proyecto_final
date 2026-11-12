from sqlalchemy.orm import Session

from backend.schemas.auth_schema import (
    CorreoRecuperacionUpdate,
    EstadoUpdate,
    RestablecerContrasena,
    RolUpdate,
    SolicitudRecuperacionContrasena,
    UsuarioLogin,
    UsuarioRegistro,
)
from backend.services.auth_service import AuthService


class AuthController:

    @staticmethod
    def login(data: UsuarioLogin, db: Session):
        return AuthService.login_service(data, db)

    @staticmethod
    def solicitar_recuperacion(
        data: SolicitudRecuperacionContrasena,
        db: Session,
    ):
        return AuthService.solicitar_recuperacion_service(data, db)

    @staticmethod
    def restablecer_contrasena(data: RestablecerContrasena, db: Session):
        return AuthService.restablecer_contrasena_service(data, db)

    @staticmethod
    def registrar(data: UsuarioRegistro, db: Session):
        return AuthService.registrar_service(data, db)

    @staticmethod
    def listar_usuarios(db: Session):
        return AuthService.listar_usuarios_service(db)

    @staticmethod
    def cambiar_estado(user_id: int, data: EstadoUpdate, db: Session):
        return AuthService.cambiar_estado_usuario_service(
            user_id,
            data.estado,
            db,
        )

    @staticmethod
    def cambiar_rol(user_id: int, data: RolUpdate, db: Session):
        return AuthService.cambiar_rol_usuario_service(
            user_id,
            data.id_rol,
            db,
        )

    @staticmethod
    def eliminar_usuario(user_id: int, db: Session):
        return AuthService.eliminar_usuario_service(user_id, db)

    @staticmethod
    def actualizar_correo_recuperacion(
        user_id: int,
        data: CorreoRecuperacionUpdate,
        db: Session,
    ):
        return AuthService.actualizar_correo_recuperacion_service(
            user_id,
            data,
            db,
        )
