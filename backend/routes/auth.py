from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/registrar', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    
    empleado = data.get('empleado')
    correo = data.get('correo_usuario')
    contrasenia = data.get('contrasenia_usuario')
    cedula = data.get('cedula_usuario')
    id_rol = data.get('id_rol', 3)
    
    if not empleado or not correo or not contrasenia or not cedula:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400
        
    try:
        existe = Usuario.query.filter_by(correo_usuario=correo).first()
        if existe:
            return jsonify({"error": "El correo ya se encuentra registrado"}), 400
            
        nuevo_usuario = Usuario(
            empleado=empleado,
            correo_usuario=correo,
            contrasenia_usuario=contrasenia,
            cedula_usuario=cedula,
            id_rol=id_rol
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({"mensaje": f"¡Trabajador {empleado} registrado exitosamente!"}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    correo = data.get('correo_usuario')
    contrasenia = data.get('contrasenia_usuario')
    
    if not correo or not contrasenia:
        return jsonify({"error": "Por favor, ingrese correo y contraseña."}), 400
        
    try:
        user = Usuario.query.filter_by(correo_usuario=correo).first()
        
        if user and user.contrasenia_usuario == contrasenia:
            rol_nombre = "jefe" if user.id_rol == 1 else "trabajador"
            
            return jsonify({
                "mensaje": "Acceso concedido",
                "usuario": {
                    "id": user.id_usuario,
                    "nombre": user.empleado,
                    "correo": user.correo_usuario,
                    "rol": rol_nombre,
                    "id_rol": user.id_rol
                }
            }), 200
            
        return jsonify({"error": "Credenciales incorrectas. Verifique e intente de nuevo."}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500