from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db
from backend.models import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/registrar', methods=['POST'])
def registrar_usuario():
    # silent=True evita que Flask falle de inmediato si el body no trae formato JSON
    data = request.get_json(silent=True) or {}
    
    # Depuración en la terminal para inspeccionar la petición recibida
    print("\n--- DEPURACIÓN PETICIÓN REGISTRO ---")
    print("Headers Content-Type:", request.headers.get('Content-Type'))
    print("Payload recibido:", data)
    print("------------------------------------\n")

    # Mapeo flexible: soporta llaves del modelo y de React
    empleado = data.get('empleado') or data.get('nombre') or data.get('nombre_completo')
    correo = data.get('correo_usuario') or data.get('correo') or data.get('email')
    contrasenia = data.get('contrasenia_usuario') or data.get('contrasena') or data.get('password')
    cedula = data.get('cedula_usuario') or data.get('cedula') or data.get('documento')
    id_rol = data.get('id_rol', 3)
    
    # Validar que ningún campo requerimiento sea nulo/vacío
    if not empleado or not correo or not contrasenia or not cedula:
        return jsonify({
            "error": "Todos los campos son obligatorios",
            "recibido": {
                "empleado": empleado,
                "correo": correo,
                "contrasenia": bool(contrasenia),
                "cedula": cedula
            }
        }), 400
        
    try:
        existe = Usuario.query.filter_by(correo_usuario=correo).first()
        if existe:
            return jsonify({"error": "El correo ya se encuentra registrado"}), 400
            
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
    data = request.get_json(silent=True) or {}
    correo = data.get('correo_usuario') or data.get('correo') or data.get('email')
    contrasenia = data.get('contrasenia_usuario') or data.get('contrasena') or data.get('password')
    
    if not correo or not contrasenia:
        return jsonify({"error": "Por favor, ingrese correo y contraseña."}), 400
        
    try:
        user = Usuario.query.filter_by(correo_usuario=correo).first()
        
        password_valida = False
        if user:
            if user.contrasenia_usuario.startswith(('pbkdf2:', 'scrypt:')):
                password_valida = check_password_hash(user.contrasenia_usuario, contrasenia)
            else:
                password_valida = (user.contrasenia_usuario == contrasenia)

        if user and password_valida:
            rol_nombre = "jefe" if user.id_rol == 1 else "trabajador"
            
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


@auth_bp.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def eliminar_usuario(id_usuario):
    try:
        user = Usuario.query.get(id_usuario)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        if user.id_rol == 1:
            return jsonify({"error": "No se puede eliminar la cuenta de Administrador principal"}), 400

        db.session.delete(user)
        db.session.commit()
        return jsonify({"mensaje": "Empleado eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500