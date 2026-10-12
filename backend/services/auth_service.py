import hmac

from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.repositories.auth_repository import AuthRepository
from backend.models.models import Rol, Usuario
from backend.security import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

class AuthService:

    @staticmethod
    def login_service(data, db: Session):
        usuario = AuthRepository.obtener_por_correo(db, data.correo)
        if not usuario or not AuthService._verify_password(
            usuario.contrasenia, data.contrasenia
        ):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

        if not AuthService._is_password_hash(usuario.contrasenia):
            usuario.contrasenia = generate_password_hash(data.contrasenia)
            db.commit()

        # --- CAMBIA ESTA LÍNEA AQUÍ MISMO ---
        if not usuario.estado or usuario.estado.upper() not in ['ACTIVO', 'APROBADO']:
            raise HTTPException(status_code=403, detail="Tu cuenta está pendiente de aprobación.")
        # ------------------------------------

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
    def registrar_service(data, db: Session):
        existe = AuthRepository.obtener_por_correo(db, data.correo)
        if existe:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

        primer_usuario = db.query(Usuario).count() == 0
        usuario_dict = {
            "empleado": data.empleado,
            "correo": data.correo,
            "contrasenia": generate_password_hash(data.contrasenia),
            "cedula_usuario": data.cedula,  # <-- Cámbialo aquí de "cedula" a "cedula_usuario"
            "id_rol": 1 if primer_usuario else 3,
            "estado": "ACTIVO" if primer_usuario else "PENDIENTE"
        }

        AuthRepository.crear_usuario(db, usuario_dict)
        if primer_usuario:
            return {
                "mensaje": "Cuenta de administrador creada. Ya puedes iniciar sesión."
            }
        return {"mensaje": "¡Usuario creado con éxito! Tu cuenta está pendiente de aprobación."}

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
        try:
            usuarios = AuthRepository.obtener_todos_los_usuarios(db)
            resultado = []
            for u in usuarios:
                rol_obj = db.query(Rol).filter(Rol.id_rol == u.id_rol).first()
                resultado.append({
                    "id_usuario": u.id_usuario,
                    "empleado": u.empleado,
                    "correo": u.correo,
                    "cedula": getattr(u, 'cedula', getattr(u, 'cedula_usuario', '')),
                    "id_rol": u.id_rol,
                    "rol": rol_obj.nombre_rol if rol_obj else "TRABAJADOR",
                    "estado": u.estado
                })
            return resultado
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def cambiar_estado_usuario_service(user_id: int, estado: str, db: Session):
        # Limpiamos y forzamos siempre el estado a mayúsculas (ej. 'ACTIVO')
        estado_limpio = estado.strip('"').strip("'").upper()
        usuario = AuthRepository.actualizar_estado_usuario(db, user_id, estado_limpio)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return {"mensaje": f"El estado del usuario fue actualizado a {estado_limpio} correctamente."}

    @staticmethod
    def eliminar_usuario_service(user_id: int, db: Session):
        usuario = AuthRepository.eliminar_usuario(db, user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return {"mensaje": "Usuario eliminado correctamente."}