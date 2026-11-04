from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from backend.controllers.produccion_controller import ProduccionController
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas.produccion_schema import (
    AvanceProcesoResponse,
    AreaCreate,
    ProcesoProduccionCreate,
    ProcesoProduccionResponse,
    OrdenProduccionCreate,
    OrdenProduccionResponse,
    RetrasoProduccionCreate,
    TrazoProduccionCreate,
    TrazoProduccionResponse,
)

router = APIRouter(
    prefix="/produccion",
    tags=["Producción"],
    dependencies=[Depends(get_current_user)],
)

@router.post(
    "/trazos",
    status_code=status.HTTP_201_CREATED,
    response_model=TrazoProduccionResponse,
)
def registrar_trazo(
    data: TrazoProduccionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return ProduccionController.registrar_trazo(data, db, id_usuario)


@router.get(
    "/trazos",
    response_model=list[TrazoProduccionResponse],
)
def listar_trazos(db: Session = Depends(get_db)):
    return ProduccionController.listar_trazos(db)


@router.post(
    "/ordenes",
    status_code=status.HTTP_201_CREATED,
    response_model=OrdenProduccionResponse,
)
@router.post(
    "/orden",
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
    response_model=OrdenProduccionResponse,
)
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


@router.get(
    "/ordenes/{id_produccion}/procesos",
    response_model=list[ProcesoProduccionResponse],
)
def listar_procesos_orden(id_produccion: int, db: Session = Depends(get_db)):
    return ProduccionController.listar_procesos(id_produccion, db)


@router.post(
    "/ordenes/{id_produccion}/avanzar",
    response_model=AvanceProcesoResponse,
)
def avanzar_etapa(
    id_produccion: int,
    data: ProcesoProduccionCreate,
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
