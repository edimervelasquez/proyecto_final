import hmac

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from backend.repositories.auth_repository import AuthRepository
from backend.models.models import Rol, Usuario
from backend.schemas.auth_schema import UsuarioLogin, UsuarioRegistro
from backend.security import create_access_token

class AuthService:

    @staticmethod
    def _commit(db: Session):
        try:
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="No se pudieron guardar los cambios de usuario.",
            ) from exc

    @staticmethod
    def login_service(data: UsuarioLogin, db: Session):
        usuario = AuthRepository.obtener_por_correo(db, data.correo)
        if not usuario or not AuthService._verify_password(
            usuario.contrasenia, data.contrasenia
        ):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

        if not AuthService._is_password_hash(usuario.contrasenia):
            usuario.contrasenia = generate_password_hash(data.contrasenia)
            AuthService._commit(db)

        if not usuario.estado or usuario.estado.upper() not in ("ACTIVO", "APROBADO"):
            raise HTTPException(status_code=403, detail="Tu cuenta está pendiente de aprobación.")

        rol_obj = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
        nombre_rol = rol_obj.nombre_rol if rol_obj else "TRABAJADOR"

        return {
            "mensaje": "Inicio de sesión exitoso.",
            "access_token": create_access_token(usuario.id_usuario, nombre_rol),
            "token_type": "bearer",
            "usuario": {
                "id_usuario": usuario.id_usuario,
                "empleado": usuario.empleado,
                "correo": usuario.correo,
                "id_rol": usuario.id_rol,
                "rol": nombre_rol,
                "estado": usuario.estado
            }
        }

    @staticmethod
    def registrar_service(data: UsuarioRegistro, db: Session):
        existe = AuthRepository.obtener_por_correo(db, data.correo)
        if existe:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

        primer_usuario = db.query(Usuario).count() == 0
        usuario_dict = {
            "empleado": data.empleado,
            "correo": data.correo,
            "contrasenia": generate_password_hash(data.contrasenia),
            "cedula_usuario": data.cedula,
            "id_rol": 1 if primer_usuario else data.id_rol,
            "estado": "ACTIVO" if primer_usuario else "PENDIENTE"
        }

        AuthRepository.crear_usuario(db, usuario_dict)
        AuthService._commit(db)
        if primer_usuario:
            return {
                "mensaje": "Cuenta de administrador creada. Ya puedes iniciar sesión."
            }
        return {
            "mensaje": (
                "¡Usuario creado con éxito! Tu cuenta está pendiente de aprobación."
            )
        }

    @staticmethod
    def _is_password_hash(password: str) -> bool:
        return password.startswith(("scrypt:", "pbkdf2:"))

    @staticmethod
    def _verify_password(stored_password: str, provided_password: str) -> bool:
        if AuthService._is_password_hash(stored_password):
            return check_password_hash(stored_password, provided_password)
        return hmac.compare_digest(stored_password, provided_password)

    @staticmethod
    def listar_usuarios_service(db: Session):
        return [
            {
                "id_usuario": usuario.id_usuario,
                "empleado": usuario.empleado,
                "correo": usuario.correo,
                "cedula": usuario.cedula_usuario,
                "id_rol": usuario.id_rol,
                "rol": nombre_rol or "TRABAJADOR",
                "estado": usuario.estado,
            }
            for usuario, nombre_rol in AuthRepository.obtener_usuarios_con_rol(db)
        ]

    @staticmethod
    def cambiar_estado_usuario_service(user_id: int, estado: str, db: Session):
        estado_limpio = estado.strip('"').strip("'").upper()
        usuario = AuthRepository.actualizar_estado_usuario(db, user_id, estado_limpio)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        AuthService._commit(db)
        return {"mensaje": f"El estado del usuario fue actualizado a {estado_limpio} correctamente."}

    @staticmethod
    def cambiar_rol_usuario_service(user_id: int, id_rol: int, db: Session):
        if id_rol not in (1, 2, 3):
            raise HTTPException(status_code=400, detail="Rol no válido.")
        usuario = AuthRepository.obtener_por_id(db, user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        if usuario.id_rol == 1 and id_rol != 1:
            administradores_activos = db.query(Usuario).filter(
                Usuario.id_rol == 1,
                Usuario.estado.in_(["ACTIVO", "APROBADO"]),
            ).count()
            if administradores_activos <= 1:
                raise HTTPException(
                    status_code=409,
                    detail="No se puede cambiar el rol del último administrador activo.",
                )
        actualizado = AuthRepository.actualizar_rol_usuario(db, user_id, id_rol)
        AuthService._commit(db)
        roles = {1: "ADMINISTRADOR", 2: "TRABAJADOR", 3: "VENDEDOR"}
        return {
            "mensaje": f"Rol actualizado a {roles[id_rol]}.",
            "id_usuario": actualizado.id_usuario,
            "id_rol": actualizado.id_rol,
        }

    @staticmethod
    def eliminar_usuario_service(user_id: int, db: Session):
        usuario = AuthRepository.eliminar_usuario(db, user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        AuthService._commit(db)
        return {"mensaje": "Usuario eliminado correctamente."}