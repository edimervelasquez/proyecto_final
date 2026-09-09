import logging
from fastapi import APIRouter, HTTPException, status
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

# Ajusta estas importaciones según cómo tengas configurado tu database.py en FastAPI
# Y reemplázalo por esto:
from backend.database import db 
from backend.models import Usuario
from backend.schemas.auth_schema import UsuarioRegistro, UsuarioLogin, EstadoUpdate

logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

router = APIRouter()

@router.post('/registrar', status_code=status.HTTP_201_CREATED)
def registrar_usuario(user_data: UsuarioRegistro):
    try:
        existe = Usuario.query.filter_by(correo_usuario=user_data.correo).first()
        if existe:
            raise HTTPException(status_code=400, detail="El correo ya se encuentra registrado")
            
        hashed_pw = generate_password_hash(user_data.contrasenia)

        nuevo_usuario = Usuario(
            empleado=user_data.empleado,
            correo_usuario=user_data.correo,
            contrasenia_usuario=hashed_pw,
            cedula_usuario=user_data.cedula,
            id_rol=user_data.id_rol,
            estado='PENDIENTE'
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        return {"mensaje": f"¡Trabajador {user_data.empleado} registrado exitosamente! Espera la aprobación del administrador."}
        
    except IntegrityError as e:
        db.session.rollback()
        logging.error(f"Error de integridad BD: {str(e)}")
        raise HTTPException(status_code=400, detail="Error de integridad. Verifique la información ingresada.")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno en el servidor.")


@router.post('/login')
def login_usuario(user_data: UsuarioLogin):
    try:
        user = Usuario.query.filter_by(correo_usuario=user_data.correo).first()
        
        password_valida = False
        if user:
            if user.contrasenia_usuario.startswith(('pbkdf2:', 'scrypt:')):
                password_valida = check_password_hash(user.contrasenia_usuario, user_data.contrasenia)
            else:
                password_valida = (user.contrasenia_usuario == user_data.contrasenia)

        if user and password_valida:
            estado_actual = getattr(user, 'estado', 'PENDIENTE')
            if estado_actual == 'PENDIENTE':
                raise HTTPException(status_code=403, detail="Tu cuenta está pendiente de aprobación.")
            if estado_actual == 'INACTIVO':
                raise HTTPException(status_code=403, detail="Tu cuenta se encuentra inactiva.")

            rol_nombre = "jefe" if user.id_rol == 1 else "trabajador"
            
            return {
                "mensaje": "Acceso concedido",
                "usuario": {
                    "id_usuario": user.id_usuario,
                    "empleado": user.empleado,
                    "correo_usuario": user.correo_usuario,
                    "rol": rol_nombre,
                    "estado": estado_actual
                }
            }
            
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error interno en login: {str(e)}")
        raise HTTPException(status_code=500, detail="Ocurrió un error al intentar iniciar sesión.")