from sqlalchemy.orm import Session

from backend.services.calidad_service import CalidadService


class CalidadController:

    @staticmethod
    def registrar_control(data, db: Session):
        return CalidadService.registrar_control(data, db)
