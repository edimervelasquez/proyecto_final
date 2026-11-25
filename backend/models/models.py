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
    empleado = Column('nombre', String(100), nullable=False)
    contrasenia = Column('password', String(255), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    correo_recuperacion = Column(String(254))
    codigo_recuperacion_hash = Column(String(64))
    codigo_recuperacion_expira = Column(Integer)
    intentos_codigo_recuperacion = Column(
        Integer, nullable=False, default=0, server_default='0'
    )
    cedula_usuario = Column(String(20))
    id_rol = Column(Integer, ForeignKey('rol.id_rol'), nullable=False)
    estado = Column(
        String(20),
        server_default='ACTIVO',
        nullable=False,
    )

class MateriaPrima(Base):
    __tablename__ = 'materia_prima'
    id_materia_prima = Column(Integer, primary_key=True)
    nombre_material = Column('nombre', String(100), nullable=False)
    referencia = Column(String(100))
    descripcion = Column(Text)
    color = Column(String(50))
    origen = Column(String(100))
    Cantidad_materiaPrima = Column(
        'stock_actual',
        Numeric(10, 2),
        nullable=False,
        default=0,
        server_default='0.00',
    )
    unidad_medida = Column(
        String(50),
        nullable=True,
        default='Metros',
        server_default='Metros',
    )
    stock_minimo = Column(
        Integer, nullable=False, default=0, server_default='0'
    )

class IngresoInsumos(Base):
    __tablename__ = 'ingreso_insumos'
    id_entrante = Column(Integer, primary_key=True, index=True)
    id_materia_prima = Column(
        Integer,
        ForeignKey('materia_prima.id_materia_prima', ondelete='CASCADE'),
        nullable=False,
    )
    cantidad_materia_prima = Column(Numeric(10, 2), nullable=False)
    proveedor = Column(String(100))
    costo_unitario = Column(Numeric(10, 2)) 
    fecha_ingreso = Column(DateTime)


class MovimientoInsumo(Base):
    __tablename__ = 'movimiento_insumo'

    id_movimiento = Column(Integer, primary_key=True)
    id_materia_prima = Column(
        Integer, ForeignKey('materia_prima.id_materia_prima'), nullable=False
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
    sku_prenda = Column(
        String(50), ForeignKey('producto_comercial.sku_prenda'), nullable=False
    )
    canal_destino = Column(String(20), nullable=False)
    costo_unitario_estimado = Column(Numeric(12, 2), nullable=False)
    cantidad_recibida = Column('cantidad', Integer, nullable=False)
    fecha_recibido = Column(
        'fecha_inicio', DateTime, server_default=func.now()
    )
    estado_general = Column(
        String(50), default='EN_PROCESO', server_default='EN_PROCESO'
    )
    id_area = Column(Integer, ForeignKey('area.id_area'))
    id_ingreso_insumos = Column(
        Integer, ForeignKey('ingreso_insumos.id_entrante')
    )
    fecha_entrega = Column(Date)
    cantidad_entregada = Column(
        Integer, default=0, server_default='0', nullable=False
    )

class Area(Base):
    __tablename__ = 'area'
    id_area = Column(Integer, primary_key=True)
    nombre_area = Column(String(100), nullable=False)
    descripcion = Column(Text)

class FichaTecnicaInsumo(Base):
    __tablename__ = 'ficha_tecnica_insumo'
    id_ficha = Column(Integer, primary_key=True)
    sku_prenda = Column(
        String(50),
        ForeignKey('producto_comercial.sku_prenda'),
        nullable=False,
    )
    id_materia_prima = Column(
        Integer, ForeignKey('materia_prima.id_materia_prima'), nullable=False
    )
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


class EtapaProduccion(Base):
    __tablename__ = 'etapa_produccion'

    id_etapa = Column(Integer, primary_key=True)
    id_produccion = Column(
        Integer,
        ForeignKey('produccion.id_produccion', ondelete='CASCADE'),
        nullable=False,
    )
    id_area_anterior = Column(Integer, ForeignKey('area.id_area'))
    id_area_nueva = Column(Integer, ForeignKey('area.id_area'), nullable=False)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_cambio = Column(DateTime, server_default=func.now())
    estado = Column(
        String(30),
        default="COMPLETADO",
        server_default="COMPLETADO",
    )
    observaciones = Column(Text)


class InventarioPrenda(Base):
    __tablename__ = 'inventario_prenda'
    __table_args__ = (
        UniqueConstraint('sku_prenda', 'ubicacion', name='uq_inventario_sku_ubicacion'),
    )

    id_inventario = Column(Integer, primary_key=True)
    sku_prenda = Column(
        String(50),
        ForeignKey('producto_comercial.sku_prenda'),
        nullable=False,
    )
    ubicacion = Column(String(30), nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)
    costo_promedio = Column(Numeric(12, 2), nullable=False, default=0)


class MovimientoPrenda(Base):
    __tablename__ = 'movimiento_prenda'

    id_movimiento = Column(Integer, primary_key=True)
    sku_prenda = Column(
        String(50),
        ForeignKey('producto_comercial.sku_prenda'),
        nullable=False,
    )
    ubicacion = Column(String(30), nullable=False)
    tipo_movimiento = Column(String(30), nullable=False)
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Numeric(12, 2), nullable=False, default=0)
    referencia = Column(String(100))
    grupo_traslado = Column(String(36))
    id_produccion = Column(Integer, ForeignKey('produccion.id_produccion'))
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
    sku_prenda = Column(
        String(50),
        ForeignKey('producto_comercial.sku_prenda'),
        nullable=False,
    )
    id_produccion = Column(Integer, ForeignKey('produccion.id_produccion'))
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


class TipoMerma(Base):
    __tablename__ = 'tipo_merma'

    id_tipo_merma = Column(Integer, primary_key=True)
    descripcion_merma = Column(String(100), nullable=False)


class Merma(Base):
    __tablename__ = 'merma'

    id_merma = Column(Integer, primary_key=True)
    id_produccion = Column(
        Integer,
        ForeignKey('produccion.id_produccion', ondelete='CASCADE'),
        nullable=False,
    )
    id_tipo_merma = Column(
        Integer, ForeignKey('tipo_merma.id_tipo_merma'), nullable=False
    )
    cantidad_sobrante = Column(Numeric(10, 2), nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())


__all__ = [
    'Area',
    'ControlCalidad',
    'DetalleVenta',
    'EtapaProduccion',
    'FichaTecnicaInsumo',
    'IngresoInsumos',
    'InventarioPrenda',
    'MateriaPrima',
    'Merma',
    'MovimientoInsumo',
    'MovimientoPrenda',
    'Produccion',
    'ProductoComercial',
    'RetrasoProduccion',
    'Rol',
    'TipoMerma',
    'Trazabilidad',
    'Usuario',
    'Venta',
]
