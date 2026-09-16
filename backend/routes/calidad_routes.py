from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.controllers.calidad_controller import CalidadController
from backend.database import get_db
from backend.schemas.calidad_schema import ControlCalidadCreate

router = APIRouter(prefix="/produccion/calidad", tags=["Calidad"])


@router.post("", status_code=status.HTTP_200_OK)
def registrar_control_calidad(
    data: ControlCalidadCreate, db: Session = Depends(get_db)
):
    return CalidadController.registrar_control(data, db)
