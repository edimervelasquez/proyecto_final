from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.repositories.auth_repository import AuthRepository
from backend.models.models import Rol  # <-- 1. Importamos el modelo Rol

class AuthService:

    @staticmethod
    def login_service(data, db: Session):
        usuario = AuthRepository.obtener_por_correo(db, data.correo)
        if not usuario or usuario.contrasenia != data.contrasenia:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
        
        # --- CAMBIA ESTA LÍNEA AQUÍ MISMO ---
        if not usuario.estado or usuario.estado.upper() not in ['ACTIVO', 'APROBADO']:
            raise HTTPException(status_code=403, detail="Tu cuenta está pendiente de aprobación.")
        # ------------------------------------

        rol_obj = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
        nombre_rol = rol_obj.nombre_rol if rol_obj else "TRABAJADOR"

        return {
            "mensaje": "Inicio de sesión exitoso.",
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

        usuario_dict = {
            "empleado": data.empleado,
            "correo": data.correo,
            "contrasenia": data.contrasenia,
            "cedula_usuario": data.cedula,  # <-- Cámbialo aquí de "cedula" a "cedula_usuario"
            "id_rol": data.id_rol,
            "estado": "PENDIENTE"
        }

        AuthRepository.crear_usuario(db, usuario_dict)
        return {"mensaje": "¡Usuario creado con éxito! Tu cuenta está pendiente de aprobación."}

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