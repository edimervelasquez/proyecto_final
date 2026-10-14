from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from backend.controllers.produccion_controller import ProduccionController
from backend.database import get_db
from backend.schemas.produccion_schema import (
    AreaCreate,
    OrdenProduccionCreate,
    RetrasoProduccionCreate,
)
from backend.schemas.comercial_schema import EtapaProduccionUpdate

router = APIRouter(prefix="/produccion", tags=["Producción"])


@router.post("/orden", status_code=status.HTTP_201_CREATED)
def registrar_orden_produccion(
    data: OrdenProduccionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return ProduccionController.registrar_orden(data, db, id_usuario)


@router.get("/actividad-reciente")
def actividad_reciente(db: Session = Depends(get_db)):
    return ProduccionController.actividad_reciente(db)


@router.get("/ordenes")
def listar_ordenes(db: Session = Depends(get_db)):
    return ProduccionController.listar_ordenes(db)


@router.get("/areas")
def listar_areas(db: Session = Depends(get_db)):
    return ProduccionController.listar_areas(db)


@router.post("/areas", status_code=status.HTTP_201_CREATED)
def crear_area(data: AreaCreate, db: Session = Depends(get_db)):
    return ProduccionController.crear_area(data, db)


@router.post("/ordenes/{id_produccion}/avanzar")
def avanzar_etapa(
    id_produccion: int,
    data: EtapaProduccionUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return ProduccionController.avanzar_etapa(
        id_produccion,
        data,
        db,
        id_usuario,
    )


@router.get("/retrasos")
def listar_retrasos(db: Session = Depends(get_db)):
    return ProduccionController.listar_retrasos(db)


@router.get("/ordenes/{id_produccion}/retrasos")
def listar_retrasos_orden(id_produccion: int, db: Session = Depends(get_db)):
    return ProduccionController.listar_retrasos_orden(id_produccion, db)


@router.post(
    "/ordenes/{id_produccion}/retrasos",
    status_code=status.HTTP_201_CREATED,
)
def registrar_retraso(
    id_produccion: int,
    data: RetrasoProduccionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return ProduccionController.registrar_retraso(
        id_produccion, data, db, id_usuario
    )


@router.post("/retrasos/{id_retraso}/reanudar")
def reanudar_produccion(
    id_retraso: int,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return ProduccionController.reanudar_produccion(
        id_retraso, db, id_usuario
    )
