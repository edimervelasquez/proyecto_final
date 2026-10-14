from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from backend.controllers.insumos_controller import InsumosController
from backend.database import get_db
from backend.schemas.insumos_schema import (
    FichaTecnicaCreate,
    IngresoInsumoCreate,
    StockMinimoUpdate,
)

router = APIRouter(prefix="/insumos", tags=["Insumos y Fichas Técnicas"])

@router.post("/ingreso", status_code=status.HTTP_201_CREATED)
def registrar_ingreso(
    data: IngresoInsumoCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return InsumosController.registrar_ingreso(data, db, id_usuario)

@router.post("/ficha-tecnica", status_code=status.HTTP_201_CREATED)
def crear_ficha(
    data: FichaTecnicaCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return InsumosController.crear_ficha_tecnica(data, db, id_usuario)


@router.get("/catalogo")
def listar_catalogo(db: Session = Depends(get_db)):
    return InsumosController.listar_catalogo(db)


@router.get("/ingresos")
def listar_ingresos(db: Session = Depends(get_db)):
    return InsumosController.listar_ingresos(db)


@router.get("/fichas")
def listar_fichas(db: Session = Depends(get_db)):
    return InsumosController.listar_fichas(db)


@router.put("/{id_materia_prima}/stock-minimo")
def actualizar_stock_minimo(
    id_materia_prima: int,
    data: StockMinimoUpdate,
    db: Session = Depends(get_db),
):
    return InsumosController.actualizar_stock_minimo(
        id_materia_prima, data.stock_minimo, db
    )


@router.get("/alertas-stock")
def listar_alertas_stock(db: Session = Depends(get_db)):
    return InsumosController.listar_alertas_stock(db)


@router.get("/movimientos")
def listar_movimientos(db: Session = Depends(get_db)):
    return InsumosController.listar_movimientos(db)