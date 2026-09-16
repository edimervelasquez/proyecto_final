from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.insumos_schema import IngresoInsumoCreate, FichaTecnicaCreate
from backend.controllers.insumos_controller import InsumosController

router = APIRouter(prefix="/insumos", tags=["Insumos y Fichas Técnicas"])

@router.post("/ingreso", status_code=status.HTTP_201_CREATED)
def registrar_ingreso(data: IngresoInsumoCreate, db: Session = Depends(get_db)):
    return InsumosController.registrar_ingreso_controller(data, db)

@router.post("/ficha-tecnica", status_code=status.HTTP_201_CREATED)
def crear_ficha(data: FichaTecnicaCreate, db: Session = Depends(get_db)):
    return InsumosController.crear_ficha_tecnica_controller(data, db)