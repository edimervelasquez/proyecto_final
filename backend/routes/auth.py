from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db
from backend.models import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/registrar', methods=['POST'])
def registrar_usuario():
    data = request.get_json() or {}
    
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
            
        # Hash seguro para la contraseña
        hashed_pw = generate_password_hash(contrasenia)

        nuevo_usuario = Usuario(
            empleado=empleado,
            correo_usuario=correo,
            contrasenia_usuario=hashed_pw,
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
    data = request.get_json() or {}
    correo = data.get('correo_usuario')
    contrasenia = data.get('contrasenia_usuario')
    
    if not correo or not contrasenia:
        return jsonify({"error": "Por favor, ingrese correo y contraseña."}), 400
        
    try:
        user = Usuario.query.filter_by(correo_usuario=correo).first()
        
        # Soporta contraseñas encriptadas con hash y texto plano previo
        password_valida = False
        if user:
            if user.contrasenia_usuario.startswith(('pbkdf2:', 'scrypt:')):
                password_valida = check_password_hash(user.contrasenia_usuario, contrasenia)
            else:
                password_valida = (user.contrasenia_usuario == contrasenia)

        if user and password_valida:
            rol_nombre = "jefe" if user.id_rol == 1 else "trabajador"
            
            # Retornamos llaves unificadas (empleado y nombre) para evitar undefined en React
            return jsonify({
                "mensaje": "Acceso concedido",
                "usuario": {
                    "id": user.id_usuario,
                    "id_usuario": user.id_usuario,
                    "nombre": user.empleado,
                    "empleado": user.empleado,
                    "correo": user.correo_usuario,
                    "correo_usuario": user.correo_usuario,
                    "rol": rol_nombre,
                    "id_rol": user.id_rol
                }
            }), 200
            
        return jsonify({"error": "Credenciales incorrectas. Verifique e intente de nuevo."}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RUTA PARA OBTENER TODOS LOS EMPLEADOS (Solo para Jefe/Admin)
@auth_bp.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        usuarios = Usuario.query.all()
        resultado = []
        for u in usuarios:
            rol_nombre = "jefe" if u.id_rol == 1 else "trabajador"
            resultado.append({
                "id": u.id_usuario,
                "id_usuario": u.id_usuario,
                "empleado": u.empleado,
                "correo": u.correo_usuario,
                "cedula": u.cedula_usuario,
                "rol": rol_nombre,
                "id_rol": u.id_rol
            })
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# RUTA PARA ELIMINAR UN EMPLEADO POR ID
@auth_bp.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def eliminar_usuario(id_usuario):
    try:
        user = Usuario.query.get(id_usuario)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        # Evitar que el administrador se elimine a sí mismo si es id_rol == 1
        if user.id_rol == 1:
            return jsonify({"error": "No se puede eliminar la cuenta de Administrador principal"}), 400

        db.session.delete(user)
        db.session.commit()
        return jsonify({"mensaje": "Empleado eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500