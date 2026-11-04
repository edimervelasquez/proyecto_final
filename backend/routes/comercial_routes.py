from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from backend.controllers.comercial_controller import ComercialController
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas.comercial_schema import (
    InventarioInicialPrendaCreate,
    PedidoCreate,
    PedidoResponse,
    ProductoPreciosUpdate,
    TrasladoPrendaCreate,
    VentaCreate,
)

router = APIRouter(
    tags=["Inventario de prendas y ventas"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/comercial/productos")
def listar_productos(db: Session = Depends(get_db)):
    return ComercialController.listar_productos(db)


@router.put("/comercial/productos/{sku}/precios")
def actualizar_precios(
    sku: str,
    data: ProductoPreciosUpdate,
    db: Session = Depends(get_db),
):
    return ComercialController.actualizar_precios(sku, data, db)


@router.get("/inventario")
def listar_inventario(db: Session = Depends(get_db)):
    return ComercialController.listar_inventario(db)


@router.get("/inventario/movimientos")
def listar_movimientos(db: Session = Depends(get_db)):
    return ComercialController.listar_movimientos(db)


@router.post("/inventario/traslados", status_code=status.HTTP_201_CREATED)
def trasladar_prendas(
    data: TrasladoPrendaCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return ComercialController.trasladar(data, db, id_usuario)


@router.post("/inventario/inicial", status_code=status.HTTP_201_CREATED)
def registrar_inventario_inicial(
    data: InventarioInicialPrendaCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return ComercialController.registrar_inventario_inicial(
        data,
        db,
        id_usuario,
    )


@router.get("/ventas")
def listar_ventas(db: Session = Depends(get_db)):
    return ComercialController.listar_ventas(db)


@router.post(
    "/ventas",
    status_code=status.HTTP_201_CREATED,
    response_model=PedidoResponse,
)
def registrar_venta(
    data: VentaCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return ComercialController.registrar_venta(data, db, id_usuario)


@router.post(
    "/pedidos",
    status_code=status.HTTP_201_CREATED,
    response_model=PedidoResponse,
    tags=["Pedidos"],
)
def registrar_pedido(
    data: PedidoCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    id_usuario = int(request.state.token_payload["sub"])
    return ComercialController.registrar_venta(
        data,
        db,
        id_usuario,
        require_production_lot=True,
    )
