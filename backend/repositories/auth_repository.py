from sqlalchemy.orm import Session
from backend.models.models import Usuario

class AuthRepository:

    @staticmethod
    def obtener_por_correo(db: Session, correo: str):
        return db.query(Usuario).filter(Usuario.correo == correo).first()

    @staticmethod
    def crear_usuario(db: Session, usuario_data: dict):
        nuevo_usuario = Usuario(**usuario_data)
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario

    @staticmethod
    def obtener_todos_los_usuarios(db: Session):
        return db.query(Usuario).all()

    @staticmethod
    def actualizar_estado_usuario(db: Session, user_id: int, nuevo_estado: str):
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if usuario:
            usuario.estado = nuevo_estado
            
            # Si el estado es aprobado/activo, le asignamos automáticamente el rol de trabajador
            if nuevo_estado in ['ACTIVO', 'APROBADO']:
                usuario.id_rol = 2  # Asegúrate de que 2 sea el id_rol de trabajador en tu tabla 'rol'
                
            db.commit()
            db.refresh(usuario)
        return usuario
    
    @staticmethod
    def eliminar_usuario(db: Session, user_id: int):
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if usuario:
            db.delete(usuario)
            db.commit()
        return usuario