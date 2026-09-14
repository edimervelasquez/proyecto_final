from sqlalchemy.orm import Session
from backend.services.auth_service import AuthService

class AuthController:

    @staticmethod
    def login(data, db: Session):
        return AuthService.login_service(data, db)

    @staticmethod
    def registrar(data, db: Session):
        return AuthService.registrar_service(data, db)

    @staticmethod
    def listar_usuarios(db: Session):
        return AuthService.listar_usuarios_service(db)

    @staticmethod
    def cambiar_estado(user_id: int, estado: str, db):
        return AuthService.cambiar_estado_usuario_service(user_id, estado, db)

    @staticmethod
    def eliminar_usuario(user_id: int, db: Session):
        return AuthService.eliminar_usuario_service(user_id, db)