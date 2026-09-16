from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.controllers.produccion_controller import ProduccionController
from backend.database import get_db
from backend.schemas.produccion_schema import OrdenProduccionCreate

router = APIRouter(prefix="/produccion", tags=["Producción"])


@router.post("/orden", status_code=status.HTTP_201_CREATED)
def registrar_orden_produccion(
    data: OrdenProduccionCreate, db: Session = Depends(get_db)
):
    return ProduccionController.registrar_orden(data, db)


@router.get("/actividad-reciente")
def actividad_reciente(db: Session = Depends(get_db)):
    return ProduccionController.actividad_reciente(db)
