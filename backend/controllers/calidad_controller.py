from sqlalchemy.orm import Session

from backend.schemas.calidad_schema import ControlCalidadCreate
from backend.services.calidad_service import CalidadService


class CalidadController:

    @staticmethod
    def registrar_control(
        data: ControlCalidadCreate,
        db: Session,
        id_usuario: int,
    ):
        return CalidadService.registrar_control(data, db, id_usuario)

    @staticmethod
    def listar_controles(db: Session):
        return CalidadService.listar_controles(db)
