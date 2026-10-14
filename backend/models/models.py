from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func
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
    stock_minimo = Column(Integer, nullable=False, default=0, server_default='0')

class IngresoInsumos(Base):
    __tablename__ = 'ingreso_insumos'
    id_entrante = Column(Integer, primary_key=True)
    id_materiaPrima = Column(Integer, ForeignKey('materia_prima.id_materiaPrima'), nullable=False)
    cantidad_materia_prima = Column(Integer, nullable=False)
    proveedor = Column(String(100))
    costo_unitario = Column(Numeric(10, 2)) 
    fecha_ingreso = Column(Date)


class MovimientoInsumo(Base):
    __tablename__ = 'movimiento_insumo'

    id_movimiento = Column(Integer, primary_key=True)
    id_materiaPrima = Column(
        Integer, ForeignKey('materia_prima.id_materiaPrima'), nullable=False
    )
    tipo_movimiento = Column(String(30), nullable=False)
    cantidad = Column(Numeric(12, 2), nullable=False)
    costo_unitario = Column(Numeric(12, 2), nullable=False, default=0)
    referencia = Column(String(100))
    id_produccion = Column(Integer, ForeignKey('produccion.id_produccion'))
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_movimiento = Column(
        DateTime, nullable=False, server_default=func.now()
    )


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


class Trazabilidad(Base):
    __tablename__ = 'trazabilidad'
    __table_args__ = (
        UniqueConstraint('tipo_registro', 'referencia', name='uq_trazabilidad_tipo_referencia'),
    )

    id_trazabilidad = Column(Integer, primary_key=True)
    tipo_registro = Column(String(30), nullable=False)
    referencia = Column(String(100), nullable=False)
    nombre_registro = Column(String(150), nullable=False)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())
    proceso = Column(String(50), nullable=False)
    estado = Column(String(50), nullable=False)
    descripcion = Column(Text)
    actualizado_por = Column(Integer, ForeignKey('usuario.id_usuario'))
    fecha_actualizacion = Column(DateTime)


class ControlCalidad(Base):
    __tablename__ = 'control_calidad'

    id_control = Column(Integer, primary_key=True)
    id_produccion = Column(
        Integer, ForeignKey('produccion.id_produccion'), nullable=False
    )
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    cantidad_optima = Column(Integer, nullable=False)
    cantidad_defectuosa = Column(Integer, nullable=False)
    observaciones = Column(String(500))
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())


class ProductoComercial(Base):
    __tablename__ = 'producto_comercial'

    sku_prenda = Column(String(50), primary_key=True)
    nombre_producto = Column(String(100), nullable=False)
    descripcion = Column(Text)
    costo_mano_obra = Column(Numeric(12, 2), nullable=False, default=0)
    precio_mayorista = Column(Numeric(12, 2), nullable=False, default=0)
    precio_detal = Column(Numeric(12, 2), nullable=False, default=0)
    activo = Column(Integer, nullable=False, default=1)


class OrdenComercial(Base):
    __tablename__ = 'orden_comercial'

    id_produccion = Column(
        Integer,
        ForeignKey('produccion.id_produccion'),
        primary_key=True,
    )
    sku_prenda = Column(String(50), nullable=False)
    canal_destino = Column(String(20), nullable=False)
    costo_unitario_estimado = Column(Numeric(12, 2), nullable=False)


class EtapaProduccion(Base):
    __tablename__ = 'etapa_produccion'

    id_etapa = Column(Integer, primary_key=True)
    id_produccion = Column(
        Integer, ForeignKey('produccion.id_produccion'), nullable=False
    )
    id_area_anterior = Column(Integer, ForeignKey('area.id_area'))
    id_area_nueva = Column(Integer, ForeignKey('area.id_area'), nullable=False)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_cambio = Column(DateTime, nullable=False, server_default=func.now())


class InventarioPrenda(Base):
    __tablename__ = 'inventario_prenda'
    __table_args__ = (
        UniqueConstraint('sku_prenda', 'ubicacion', name='uq_inventario_sku_ubicacion'),
    )

    id_inventario = Column(Integer, primary_key=True)
    sku_prenda = Column(String(50), nullable=False)
    ubicacion = Column(String(30), nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)
    costo_promedio = Column(Numeric(12, 2), nullable=False, default=0)


class MovimientoPrenda(Base):
    __tablename__ = 'movimiento_prenda'

    id_movimiento = Column(Integer, primary_key=True)
    sku_prenda = Column(String(50), nullable=False)
    ubicacion = Column(String(30), nullable=False)
    tipo_movimiento = Column(String(30), nullable=False)
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Numeric(12, 2), nullable=False, default=0)
    referencia = Column(String(100))
    grupo_traslado = Column(String(36))
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_movimiento = Column(DateTime, nullable=False, server_default=func.now())


class Venta(Base):
    __tablename__ = 'venta'

    id_venta = Column(Integer, primary_key=True)
    canal = Column(String(20), nullable=False)
    cliente = Column(String(150))
    fecha_venta = Column(DateTime, nullable=False, server_default=func.now())
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    total = Column(Numeric(14, 2), nullable=False, default=0)


class DetalleVenta(Base):
    __tablename__ = 'detalle_venta'

    id_detalle = Column(Integer, primary_key=True)
    id_venta = Column(Integer, ForeignKey('venta.id_venta'), nullable=False)
    sku_prenda = Column(String(50), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    costo_unitario = Column(Numeric(12, 2), nullable=False)


class RetrasoProduccion(Base):
    __tablename__ = 'retraso_produccion'

    id_retraso = Column(Integer, primary_key=True)
    id_produccion = Column(
        Integer, ForeignKey('produccion.id_produccion'), nullable=False
    )
    id_area = Column(Integer, ForeignKey('area.id_area'), nullable=False)
    id_usuario_inicio = Column(
        Integer, ForeignKey('usuario.id_usuario'), nullable=False
    )
    motivo = Column(String(80), nullable=False)
    detalle = Column(Text)
    fecha_inicio = Column(DateTime, nullable=False, server_default=func.now())
    fecha_fin = Column(DateTime)
    id_usuario_reanuda = Column(
        Integer, ForeignKey('usuario.id_usuario')
    )