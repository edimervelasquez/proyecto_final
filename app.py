from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Sergio3650270.@localhost/yullita_creaciones_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)





class Rol(db.Model):
    __tablename__ = 'rol'
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    empleado = db.Column(db.String(100), nullable=False)
    contrasenia_usuario = db.Column(db.String(255), nullable=False)
    correo_usuario = db.Column(db.String(100), unique=True, nullable=False)
    cedula_usuario = db.Column(db.String(20), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False)

class MateriaPrima(db.Model):
    __tablename__ = 'materia_prima'
    id_materiaPrima = db.Column(db.Integer, primary_key=True)
    nombre_material = db.Column(db.String(100), nullable=False) # Agregado para identificar el insumo
    Cantidad_materiaPrima = db.Column(db.Integer, nullable=False)

class IngresoInsumos(db.Model):
    __tablename__ = 'ingreso_insumos'
    id_entrante = db.Column(db.Integer, primary_key=True)
    id_materiaPrima = db.Column(db.Integer, db.ForeignKey('materia_prima.id_materiaPrima'), nullable=False)
    cantidad_materia_prima = db.Column(db.Integer, nullable=False)
    # Campos sugeridos para HU-001:
    proveedor = db.Column(db.String(100))
    costo_unitario = db.Column(db.Numeric(10, 2)) 
    fecha_ingreso = db.Column(db.Date)

class Produccion(db.Model):
    __tablename__ = 'produccion'
    id_produccion = db.Column(db.Integer, primary_key=True)
    id_area = db.Column(db.Integer, db.ForeignKey('area.id_area'), nullable=False)
    
    
    id_ingreso_insumos = db.Column(db.Integer, db.ForeignKey('ingreso_insumos.id_entrante'), nullable=False)
    
    fecha_recibido = db.Column(db.Date, nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    cantidad_recibida = db.Column(db.Integer, nullable=False)
    cantidad_entregada = db.Column(db.Integer, default=0)

class Programacion(db.Model):
    __tablename__ = 'programacion'
    id_programacion = db.Column(db.Integer, primary_key=True)
    id_produccion = db.Column(db.Integer, db.ForeignKey('produccion.id_produccion'), nullable=False)
    fecha = db.Column(db.Date)
    turno = db.Column(db.String(20))

class ProgramacionUsuario(db.Model):
    __tablename__ = 'programacion_usuario'
    __table_args__ = {'extend_existing': True}  # <-- Asegúrate de que esta línea esté idéntica

    id_programacion = db.Column(db.Integer, primary_key=True, default=1)
    id_rol = db.Column(db.Integer, primary_key=True, default=3)
    
    cantidad_defectuosa = db.Column(db.Integer, default=0)
    cantidad_recibida = db.Column(db.Integer, default=0)
    cantidad_entregada = db.Column(db.Integer, default=0)

class Prendas(db.Model):
    __tablename__ = 'prendas'
    id_prenda = db.Column(db.Integer, primary_key=True)
    id_produccion = db.Column(db.Integer, db.ForeignKey('produccion.id_produccion'), nullable=False)
    cantidad_recibida = db.Column(db.Integer)
    SKU_prenda = db.Column(db.String(50), unique=True)

class Area(db.Model):
    __tablename__ = 'area'
    id_area = db.Column(db.Integer, primary_key=True)
    id_produccion = db.Column(db.Integer) 
    tipo_turno = db.Column(db.String(20))
    nombre_area = db.Column(db.String(50))

class FichaTecnicaInsumo(db.Model):
    __tablename__ = 'ficha_tecnica_insumo'
    id_ficha = db.Column(db.Integer, primary_key=True)
    sku_prenda = db.Column(db.String(50), nullable=False) 
    id_materiaPrima = db.Column(db.Integer, db.ForeignKey('materia_prima.id_materiaPrima'), nullable=False)
    cantidad_estimada = db.Column(db.Numeric(10, 2), nullable=False) 



@app.route('/', methods=['GET'])
def index():
    return jsonify({"mensaje": "Servidor de Creaciones Yullita Corriendo con Éxito"})

# --- ENDPOINTS PARA HISTORIAS DE USUARIO ---

# HU-001: Registrar la entrada de insumos / materia prima
@app.route('/api/insumos/ingreso', methods=['POST'])
def registrar_ingreso_insumo():
    data = request.get_json()
    
    # Validar que vengan los datos obligatorios
    if not data or 'id_materiaPrima' not in data or 'cantidad' not in data:
        return jsonify({"error": "Datos incompletos. Se requiere id_materiaPrima y cantidad"}), 400
    
    try:
        # 1. Registrar el movimiento en la tabla 'ingreso_insumos'
        nuevo_ingreso = IngresoInsumos(
            id_materiaPrima=data['id_materiaPrima'],
            cantidad_materia_prima=data['cantidad'],
            proveedor=data.get('proveedor', 'Proveedor Genérico'),
            costo_unitario=data.get('costo_unitario', 0.0),
            fecha_ingreso=data.get('fecha_ingreso') # Debe venir en formato YYYY-MM-DD
        )
        db.session.add(nuevo_ingreso)
        
        # 2. Actualizar el stock actual en la tabla 'materia_prima'
        material = MateriaPrima.query.get(data['id_materiaPrima'])
        if material:
            material.Cantidad_materiaPrima += int(data['cantidad'])
        else:
            return jsonify({"error": "La materia prima especificada no existe en el catálogo"}), 44
        
        # Confirmar los cambios en la Base de Datos
        db.session.commit()
        
        return jsonify({
            "mensaje": "Ingreso de materia prima registrado correctamente",
            "nuevo_stock": material.Cantidad_materiaPrima
        }), 201
        
    except Exception as e:
        db.session.rollback() # Cancela la operación si hay error
        return jsonify({"error": str(e)}), 500

# HU-002: Calcular y Guardar Ficha Técnica con Costeo Dinámico
@app.route('/api/ficha-tecnica', methods=['POST'])
def crear_ficha_tecnica():
    data = request.get_json()
    
    sku_prenda = data.get('sku_prenda')
    insumos = data.get('insumos', []) # Lista de { id_materiaPrima, cantidad_estimada }
    costo_mano_obra = float(data.get('costo_mano_obra', 0.0))
    
    if not sku_prenda or not insumos:
        return jsonify({"error": "Datos incompletos. Se requiere SKU de prenda e insumos."}), 400
        
    try:
        costo_total_insumos = 0.0
        detalles_guardados = []
        
        for insumo in insumos:
            id_mp = insumo['id_materiaPrima']
            cant = float(insumo['cantidad_estimada'])
            
            # Buscamos el precio en los últimos ingresos de este material para simular el costo real
            ultimo_ingreso = IngresoInsumos.query.filter_by(id_materiaPrima=id_mp).order_by(IngresoInsumos.id_entrante.desc()).first()
            precio_unitario = float(ultimo_ingreso.costo_unitario) if ultimo_ingreso and ultimo_ingreso.costo_unitario else 5000.0 # Valor por defecto si no hay compras
            
            costo_parcial = cant * precio_unitario
            costo_total_insumos += costo_parcial
            
            # Guardamos la receta en la base de datos
            nueva_linea = FichaTecnicaInsumo(
                sku_prenda=sku_prenda,
                id_materiaPrima=id_mp,
                cantidad_estimada=cant
            )
            db.session.add(nueva_linea)
            detalles_guardados.append({
                "id_materiaPrima": id_mp,
                "cantidad": cant,
                "costo_estimado": costo_parcial
            })
            
        costo_fabricacion_base = costo_total_insumos + costo_mano_obra
        
        if costo_fabricacion_base <= 0:
            return jsonify({"error": "El costo base no puede ser cero."}), 400
            
        db.session.commit()
        
        return jsonify({
            "mensaje": f"Ficha técnica para {sku_prenda} guardada con éxito.",
            "costo_materiales": costo_total_insumos,
            "costo_mano_obra": costo_mano_obra,
            "costo_total_fabricacion": costo_fabricacion_base
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# HU-003: Registrar Orden de Producción y Descontar Inventario Automáticamente
@app.route('/api/produccion/orden', methods=['POST'])
def registrar_orden_produccion():
    data = request.get_json()
    
    # Capturamos los datos requeridos según tu DER
    id_area = data.get('id_area') # Área que recibe el lote (ej: Corte, Confección)
    sku_prenda = data.get('sku_prenda') # Qué diseño se va a fabricar
    cantidad_a_producir = data.get('cantidad_a_producir') # Cuántas unidades
    fecha_entrega = data.get('fecha_entrega') # Para cuándo se necesita
    
    if not all([id_area, sku_prenda, cantidad_a_producir, fecha_entrega]):
        return jsonify({"error": "Faltan campos obligatorios para registrar la orden."}), 400
        
    try:
        cantidad_a_producir = int(cantidad_a_producir)
        if cantidad_a_producir <= 0:
            return jsonify({"error": "La cantidad a producir debe ser mayor a cero."}), 400

        # 1. Buscar la "receta" (insumos) de esta prenda en la Ficha Técnica
        insumos_receta = FichaTecnicaInsumo.query.filter_by(sku_prenda=sku_prenda).all()
        
        if not insumos_receta:
            return jsonify({"error": f"No se encontró una Ficha Técnica registrada para el SKU: {sku_prenda}. Primero créala."}), 404
            
        # 2. VALIDACIÓN PREVIA: Verificar si hay suficiente stock de TODO antes de restar nada
        for item in insumos_receta:
            material = MateriaPrima.query.get(item.id_materiaPrima)
            if not material:
                return jsonify({"error": f"El material con ID {item.id_materiaPrima} requerido por la prenda no existe en el catálogo."}), 404
                
            cantidad_requerida_total = float(item.cantidad_estimada) * cantidad_a_producir
            
            # Comprobación de quiebre de stock
            if float(material.Cantidad_materiaPrima) < cantidad_requerida_total:
                return jsonify({
                    "error": f"Falta material para la orden. El insumo '{material.nombre_material}' (ID: {material.id_materiaPrima}) tiene stock de {material.Cantidad_materiaPrima}, pero requieres {cantidad_requerida_total} para este lote."
                }), 400

        # 3. PROCESAMIENTO: Si todo está en orden, descontamos el stock e insertamos la producción
        for item in insumos_receta:
            material = MateriaPrima.query.get(item.id_materiaPrima)
            cantidad_requerida_total = float(item.cantidad_estimada) * cantidad_a_producir
            
            # Descontamos directamente de la tabla general
            material.Cantidad_materiaPrima = float(material.Cantidad_materiaPrima) - cantidad_requerida_total

    

        nueva_orden = Produccion(
            id_area=id_area,
            id_ingreso_insumos=1, # <--- Agregamos este ID por defecto para cumplir la restricción del DER
            fecha_recibido=db.func.current_date(),
            fecha_entrega=fecha_entrega,
            cantidad_recibida=cantidad_a_producir,
            cantidad_entregada=0
        )
        
        db.session.add(nueva_orden)
        
        # Confirmamos la transacción completa en MySQL
        db.session.commit()
        
        return jsonify({
            "mensaje": f"¡Orden de producción para {cantidad_a_producir} unidades de {sku_prenda} iniciada con éxito!",
            "estado": "Materiales descontados del inventario correctamente."
        }), 201
        
    except Exception as e:
        db.session.rollback() # Si algo falla, cancela los descuentos para no dañar los datos
        return jsonify({"error": str(e)}), 500

# HU-004 / HU-005: Registrar Control de Calidad y Cierre de Lote Simplificado
@app.route('/api/produccion/calidad', methods=['POST'])
def registrar_control_calidad():
    data = request.get_json()
    
    id_produccion = data.get('id_produccion')
    cantidad_optima = data.get('cantidad_optima')
    cantidad_defectuosa = data.get('cantidad_defectuosa')
    
    if id_produccion is None or cantidad_optima is None or cantidad_defectuosa is None:
        return jsonify({"error": "Datos incompletos. Se requiere id_produccion, cantidad_optima y cantidad_defectuosa."}), 400
        
    try:
        id_produccion = int(id_produccion)
        cantidad_optima = int(cantidad_optima)
        cantidad_defectuosa = int(cantidad_defectuosa)
        
        # 1. Buscar la orden de producción existente
        orden = Produccion.query.get(id_produccion)
        if not orden:
            return jsonify({"error": f"No se encontró ninguna orden de producción con el ID {id_produccion}."}), 404
            
        # 2. Validación: No procesar más de lo recibido
        total_procesado = cantidad_optima + cantidad_defectuosa
        if total_procesado > orden.cantidad_recibida:
            return jsonify({
                "error": f"Inconsistencia: El lote recibió {orden.cantidad_recibida} unidades, intentas reportar {total_procesado}."
            }), 400
            
        # 3. Actualizar la tabla 'produccion' directamente con el resultado real
        orden.cantidad_entregada = cantidad_optima
        
        # Guardamos de forma segura en MySQL sin tocar la tabla intermedia
        db.session.commit()
        
        return jsonify({
            "mensaje": f"¡Control de calidad para la Orden #{id_produccion} guardado exitosamente!",
            "unidades_aprobadas": cantidad_optima,
            "unidades_defectuosas": cantidad_defectuosa,
            "estado": "Lote cerrado y listo para distribución."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
        # 3. Actualizar la tabla 'produccion' con las prendas listas para entregar
        orden.cantidad_entregada = cantidad_optima
        
        # 4. Registrar el reporte detallado de fallas en la tabla 'programacion_usuario' (según tu DER)
        # Como es una tabla intermedia, simulamos o usamos el id_rol general para cumplir la restricción
        reporte_calidad = ProgramacionUsuario(
            id_programacion=1, # Se asocia a la programación base por defecto
            id_rol=3,          # ID 3 que corresponde al 'Jefe de Calidad' que insertamos en las semillas
            cantidad_recibida=orden.cantidad_recibida,
            cantidad_entregada=cantidad_optima,
            cantidad_defectuosa=cantidad_defectuosa
        )
        db.session.add(reporte_calidad)
        
        # Confirmamos los cambios de forma segura en MySQL
        db.session.commit()
        
        return jsonify({
            "mensaje": f"¡Control de calidad para la Orden #{id_produccion} guardado exitosamente!",
            "unidades_aprobadas": cantidad_optima,
            "unidades_defectuosas": cantidad_defectuosa,
            "estado": "Lote cerrado y listo para distribución."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/dashboard/rendimiento', methods=['GET'])
def obtener_rendimiento():
    try:
        ordenes = Produccion.query.all()
        
        total_recibido = sum(o.cantidad_recibida for o in ordenes)
        total_optimo = sum(o.cantidad_entregada for o in ordenes)
        
        # Consultamos las mermas/defectuosas acumuladas de las órdenes
        # Si tienes mermas registradas directo en producción las sumamos, si no, calculamos la diferencia
        total_defectuoso = sum((o.cantidad_recibida - o.cantidad_entregada) for o in ordenes if o.cantidad_entregada is not None and o.cantidad_entregada > 0)
        
        # --- CÁLCULO FINANCIERO ---
        # Simulamos un precio promedio por prenda infantil (ej: $35,000 COP) 
        # o puedes extraerlo dinámicamente si tu modelo 'Prendas' tiene el campo precio.
        precio_unitario_promedio = 35000 
        
        # El total producido representa el valor de las prendas óptimas listas para vender
        total_dinero_producido = total_optimo * precio_unitario_promedio
        
        # Porcentaje de efectividad operativa
        porcentaje_eficiencia = 100.0
        if total_recibido > 0:
            porcentaje_eficiencia = round((total_optimo / total_recibido) * 100, 1)

        return jsonify({
            "total_recibido": total_recibido,
            "total_optimo": total_optimo,
            "total_defectuoso": total_defectuoso,
            "eficiencia": porcentaje_eficiencia,
            "precio_unitario": precio_unitario_promedio,
            "total_monetario": total_dinero_producido
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ==========================================
#   MÓDULO DE AUTENTICACIÓN Y ROLES (SIES)
# ==========================================

@app.route('/api/auth/registrar', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    
    empleado = data.get('empleado')
    correo = data.get('correo_usuario')
    contrasenia = data.get('contrasenia_usuario')
    cedula = data.get('cedula_usuario')
    id_rol = data.get('id_rol', 3) # Por defecto 3 = Trabajador si no se envía
    
    if not empleado or not correo or not contrasenia or not cedula:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400
        
    try:
        # Verificamos si el correo ya existe
        existe = Usuario.query.filter_by(correo_usuario=correo).first()
        if existe:
            return jsonify({"error": "El correo ya se encuentra registrado"}), 400
            
        # Creamos el nuevo trabajador en la base de datos
        nuevo_usuario = Usuario(
            empleado=empleado,
            correo_usuario=correo,
            contrasenia_usuario=contrasenia, # Nota: Para producción del SENA se recomienda encriptar, aquí va directo para pruebas rápidas
            cedula_usuario=cedula,
            id_rol=id_rol
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({"mensaje": f"¡Trabajador {empleado} registrado exitosamente!"}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    correo = data.get('correo_usuario')
    contrasenia = data.get('contrasenia_usuario')
    
    if not correo or not contrasenia:
        return jsonify({"error": "Por favor, ingrese correo y contraseña."}), 400
        
    try:
        # Buscamos por tu columna correo_usuario
        user = Usuario.query.filter_by(correo_usuario=correo).first()
        
        if user and user.contrasenia_usuario == contrasenia:
            # Determinamos el tipo de acceso de forma sencilla según el id_rol
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
    
if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)