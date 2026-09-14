from sqlalchemy.orm import Session
from backend.services.insumos_service import InsumosService

class InsumosController:

    @staticmethod
    def registrar_ingreso_controller(data, db: Session):
        return InsumosService.procesar_ingreso_insumo(data, db)

    @staticmethod
    def crear_ficha_tecnica_controller(data, db: Session):
        return InsumosService.procesar_ficha_tecnica(data, db)