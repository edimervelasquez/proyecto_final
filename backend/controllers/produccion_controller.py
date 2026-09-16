from sqlalchemy.orm import Session

from backend.services.produccion_service import ProduccionService


class ProduccionController:

    @staticmethod
    def registrar_orden(data, db: Session):
        return ProduccionService.registrar_orden(data, db)

    @staticmethod
    def actividad_reciente(db: Session):
        return ProduccionService.obtener_actividad_reciente(db)
