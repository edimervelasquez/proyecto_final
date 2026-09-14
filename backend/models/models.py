from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Date
from backend.database import Base

class Rol(Base):
    __tablename__ = 'rol'
    id_rol = Column(Integer, primary_key=True)
    nombre_rol = Column(String(50), nullable=False)

class Usuario(Base):
    __tablename__ = 'usuario'
    id_usuario = Column(Integer, primary_key=True)
    empleado = Column(String(100), nullable=False)
    contrasenia = Column('contrasenia_usuario', String(255), nullable=False)
    correo = Column('correo_usuario', String(100), unique=True, nullable=False)
    cedula_usuario = Column(String(20), nullable=False)
    id_rol = Column(Integer, ForeignKey('rol.id_rol'), nullable=False)
    estado = Column(String(20), default='PENDIENTE')

class MateriaPrima(Base):
    __tablename__ = 'materia_prima'
    id_materiaPrima = Column(Integer, primary_key=True)
    nombre_material = Column(String(100), nullable=False)
    Cantidad_materiaPrima = Column(Integer, nullable=False)

class IngresoInsumos(Base):
    __tablename__ = 'ingreso_insumos'
    id_entrante = Column(Integer, primary_key=True)
    id_materiaPrima = Column(Integer, ForeignKey('materia_prima.id_materiaPrima'), nullable=False)
    cantidad_materia_prima = Column(Integer, nullable=False)
    proveedor = Column(String(100))
    costo_unitario = Column(Numeric(10, 2)) 
    fecha_ingreso = Column(Date)

class Produccion(Base):
    __tablename__ = 'produccion'
    id_produccion = Column(Integer, primary_key=True)
    id_area = Column(Integer, ForeignKey('area.id_area'), nullable=False)
    id_ingreso_insumos = Column(Integer, ForeignKey('ingreso_insumos.id_entrante'), nullable=False)
    fecha_recibido = Column(Date, nullable=False)
    fecha_entrega = Column(Date, nullable=False)
    cantidad_recibida = Column(Integer, nullable=False)
    cantidad_entregada = Column(Integer, default=0)

class Programacion(Base):
    __tablename__ = 'programacion'
    id_programacion = Column(Integer, primary_key=True)
    id_produccion = Column(Integer, ForeignKey('produccion.id_produccion'), nullable=False)
    fecha = Column(Date)
    turno = Column(String(20))

class ProgramacionUsuario(Base):
    __tablename__ = 'programacion_usuario'
    __table_args__ = {'extend_existing': True}

    id_programacion = Column(Integer, primary_key=True, default=1)
    id_rol = Column(Integer, primary_key=True, default=3)
    cantidad_defectuosa = Column(Integer, default=0)
    cantidad_recibida = Column(Integer, default=0)
    cantidad_entregada = Column(Integer, default=0)

class Prendas(Base):
    __tablename__ = 'prendas'
    id_prenda = Column(Integer, primary_key=True)
    id_produccion = Column(Integer, ForeignKey('produccion.id_produccion'), nullable=False)
    cantidad_recibida = Column(Integer)
    SKU_prenda = Column(String(50), unique=True)

class Area(Base):
    __tablename__ = 'area'
    id_area = Column(Integer, primary_key=True)
    id_produccion = Column(Integer) 
    tipo_turno = Column(String(20))
    nombre_area = Column(String(50))

class FichaTecnicaInsumo(Base):
    __tablename__ = 'ficha_tecnica_insumo'
    id_ficha = Column(Integer, primary_key=True)
    sku_prenda = Column(String(50), nullable=False) 
    id_materiaPrima = Column(Integer, ForeignKey('materia_prima.id_materiaPrima'), nullable=False)
    cantidad_estimada = Column(Numeric(10, 2), nullable=False)