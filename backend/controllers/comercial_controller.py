from sqlalchemy.orm import Session

from backend.schemas.comercial_schema import (
    InventarioInicialPrendaCreate,
    PedidoCreate,
    ProductoPreciosUpdate,
    TrasladoPrendaCreate,
    VentaCreate,
)
from backend.services.comercial_service import ComercialService


class ComercialController:

    @staticmethod
    def listar_productos(db: Session):
        return ComercialService.listar_productos(db)

    @staticmethod
    def actualizar_precios(sku: str, data: ProductoPreciosUpdate, db: Session):
        return ComercialService.actualizar_precios(sku, data, db)

    @staticmethod
    def listar_inventario(db: Session):
        return ComercialService.listar_inventario(db)

    @staticmethod
    def listar_movimientos(db: Session):
        return ComercialService.listar_movimientos(db)

    @staticmethod
    def trasladar(
        data: TrasladoPrendaCreate,
        db: Session,
        id_usuario: int,
    ):
        return ComercialService.trasladar(data, db, id_usuario)

    @staticmethod
    def registrar_inventario_inicial(
        data: InventarioInicialPrendaCreate,
        db: Session,
        id_usuario: int,
    ):
        return ComercialService.registrar_inventario_inicial(
            data,
            db,
            id_usuario,
        )

    @staticmethod
    def listar_ventas(db: Session):
        return ComercialService.listar_ventas(db)

    @staticmethod
    def registrar_venta(
        data: VentaCreate | PedidoCreate,
        db: Session,
        id_usuario: int,
        require_production_lot: bool = False,
    ):
        return ComercialService.registrar_venta(
            data,
            db,
            id_usuario,
            require_production_lot=require_production_lot,
        )
