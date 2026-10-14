from sqlalchemy import case, func
from sqlalchemy.orm import Session

from backend.models.models import (
    Area,
    DetalleVenta,
    InventarioPrenda,
    MovimientoPrenda,
    OrdenComercial,
    ProductoComercial,
    Produccion,
    Usuario,
    Venta,
)


class ComercialRepository:

    @staticmethod
    def producto(db: Session, sku: str):
        return db.query(ProductoComercial).filter(
            ProductoComercial.sku_prenda == sku
        ).first()

    @staticmethod
    def actualizar_precios(
        db: Session,
        sku: str,
        precio_mayorista: float,
        precio_detal: float,
        costo_mano_obra: float,
    ):
        producto = ComercialRepository.producto(db, sku)
        if producto:
            producto.precio_mayorista = precio_mayorista
            producto.precio_detal = precio_detal
            producto.costo_mano_obra = costo_mano_obra
        return producto

    @staticmethod
    def productos(db: Session):
        return db.query(ProductoComercial).filter(
            ProductoComercial.activo == 1
        ).order_by(ProductoComercial.nombre_producto).all()

    @staticmethod
    def stock(db: Session, sku: str, ubicacion: str, lock: bool = False):
        query = db.query(InventarioPrenda).filter(
            InventarioPrenda.sku_prenda == sku,
            InventarioPrenda.ubicacion == ubicacion,
        )
        return query.with_for_update().first() if lock else query.first()

    @staticmethod
    def stocks(db: Session):
        return db.query(InventarioPrenda).order_by(
            InventarioPrenda.sku_prenda, InventarioPrenda.ubicacion
        ).all()

    @staticmethod
    def movimientos(db: Session, limite: int = 300):
        return db.query(
            MovimientoPrenda,
            Usuario.empleado,
        ).join(
            Usuario, Usuario.id_usuario == MovimientoPrenda.id_usuario
        ).order_by(
            MovimientoPrenda.fecha_movimiento.desc()
        ).limit(limite).all()

    @staticmethod
    def crear_stock(db: Session, sku: str, ubicacion: str):
        stock = InventarioPrenda(
            sku_prenda=sku,
            ubicacion=ubicacion,
            cantidad=0,
        )
        db.add(stock)
        db.flush()
        return stock

    @staticmethod
    def movimiento(db: Session, data: dict):
        movimiento = MovimientoPrenda(**data)
        db.add(movimiento)
        return movimiento

    @staticmethod
    def tiene_movimientos(db: Session, sku: str, ubicacion: str):
        return db.query(MovimientoPrenda.id_movimiento).filter(
            MovimientoPrenda.sku_prenda == sku,
            MovimientoPrenda.ubicacion == ubicacion,
        ).first() is not None

    @staticmethod
    def crear_venta(db: Session, canal: str, cliente: str, id_usuario: int):
        venta = Venta(
            canal=canal,
            cliente=cliente,
            id_usuario=id_usuario,
            total=0,
        )
        db.add(venta)
        db.flush()
        return venta

    @staticmethod
    def crear_detalle_venta(db: Session, data: dict):
        detalle = DetalleVenta(**data)
        db.add(detalle)
        return detalle

    @staticmethod
    def ventas(db: Session, limite: int = 200):
        return db.query(Venta, Usuario.empleado).join(
            Usuario, Usuario.id_usuario == Venta.id_usuario
        ).order_by(Venta.fecha_venta.desc()).limit(limite).all()

    @staticmethod
    def detalles_venta(db: Session, id_venta: int):
        return db.query(DetalleVenta).filter(
            DetalleVenta.id_venta == id_venta
        ).all()

    @staticmethod
    def resumen_ventas(db: Session):
        total, mayorista, detal = db.query(
            func.coalesce(func.sum(Venta.total), 0),
            func.coalesce(
                func.sum(
                    case((Venta.canal == "MAYORISTA", Venta.total), else_=0)
                ),
                0,
            ),
            func.coalesce(
                func.sum(case((Venta.canal == "DETAL", Venta.total), else_=0)),
                0,
            ),
        ).one()
        costo = db.query(
            func.coalesce(
                func.sum(DetalleVenta.cantidad * DetalleVenta.costo_unitario),
                0,
            )
        ).scalar()
        return total, mayorista, detal, costo or 0

    @staticmethod
    def orden_comercial(db: Session, id_produccion: int):
        return db.query(OrdenComercial).filter(
            OrdenComercial.id_produccion == id_produccion
        ).first()

    @staticmethod
    def guardar_orden_comercial(db: Session, data: dict):
        registro = OrdenComercial(**data)
        db.add(registro)
        return registro

    @staticmethod
    def orden(db: Session, id_produccion: int, lock: bool = False):
        query = db.query(Produccion).filter(
            Produccion.id_produccion == id_produccion
        )
        return query.with_for_update().first() if lock else query.first()

    @staticmethod
    def area(db: Session, id_area: int):
        return db.query(Area).filter(Area.id_area == id_area).first()
