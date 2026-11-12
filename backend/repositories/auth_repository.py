from sqlalchemy.orm import Session
from backend.models.models import Rol, Usuario

class AuthRepository:

    @staticmethod
    def obtener_por_id(db: Session, user_id: int):
        return db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

    @staticmethod
    def obtener_por_correo(db: Session, correo: str):
        return db.query(Usuario).filter(Usuario.correo == correo).first()

    @staticmethod
    def obtener_por_correo_para_actualizacion(db: Session, correo: str):
        return (
            db.query(Usuario)
            .filter(Usuario.correo == correo)
            .with_for_update()
            .first()
        )

    @staticmethod
    def crear_usuario(db: Session, usuario_data: dict):
        nuevo_usuario = Usuario(**usuario_data)
        db.add(nuevo_usuario)
        return nuevo_usuario

    @staticmethod
    def obtener_usuarios_con_rol(db: Session):
        return (
            db.query(Usuario, Rol.nombre_rol)
            .outerjoin(Rol, Rol.id_rol == Usuario.id_rol)
            .order_by(Usuario.id_usuario)
            .all()
        )

    @staticmethod
    def actualizar_estado_usuario(db: Session, user_id: int, nuevo_estado: str):
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if usuario:
            usuario.estado = nuevo_estado
        return usuario

    @staticmethod
    def actualizar_rol_usuario(db: Session, user_id: int, id_rol: int):
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if usuario:
            usuario.id_rol = id_rol
        return usuario
    
    @staticmethod
    def eliminar_usuario(db: Session, user_id: int):
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if usuario:
            db.delete(usuario)
        return usuario