from sqlalchemy.orm import Session

from backend.schemas.insumos_schema import (
    FichaTecnicaCreate,
    IngresoInsumoCreate,
)
from backend.services.insumos_service import InsumosService


class InsumosController:

    @staticmethod
    def registrar_ingreso(
        data: IngresoInsumoCreate,
        db: Session,
        id_usuario: int,
    ):
        return InsumosService.procesar_ingreso_insumo(data, db, id_usuario)

    @staticmethod
    def crear_ficha_tecnica(
        data: FichaTecnicaCreate,
        db: Session,
        id_usuario: int,
    ):
        return InsumosService.procesar_ficha_tecnica(data, db, id_usuario)

    @staticmethod
    def listar_catalogo(db: Session):
        return InsumosService.listar_catalogo(db)

    @staticmethod
    def listar_ingresos(db: Session):
        return InsumosService.listar_ingresos(db)

    @staticmethod
    def listar_fichas(db: Session):
        return InsumosService.listar_fichas(db)

    @staticmethod
    def actualizar_stock_minimo(
        id_materia_prima: int, stock_minimo: int, db: Session
    ):
        return InsumosService.actualizar_stock_minimo(
            id_materia_prima, stock_minimo, db
        )

    @staticmethod
    def listar_alertas_stock(db: Session):
        return InsumosService.listar_alertas_stock(db)

    @staticmethod
    def listar_movimientos(db: Session):
        return InsumosService.listar_movimientos(db)
