from backend.database import db

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
    nombre_material = db.Column(db.String(100), nullable=False)
    Cantidad_materiaPrima = db.Column(db.Integer, nullable=False)

class IngresoInsumos(db.Model):
    __tablename__ = 'ingreso_insumos'
    id_entrante = db.Column(db.Integer, primary_key=True)
    id_materiaPrima = db.Column(db.Integer, db.ForeignKey('materia_prima.id_materiaPrima'), nullable=False)
    cantidad_materia_prima = db.Column(db.Integer, nullable=False)
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
    __table_args__ = {'extend_existing': True}

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