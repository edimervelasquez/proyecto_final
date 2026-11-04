from typing import Literal, List

from pydantic import BaseModel, Field


class VentaDetalleCreate(BaseModel):
    sku_prenda: str = Field(..., min_length=1, max_length=50)
    cantidad: int = Field(..., gt=0)
    id_produccion: int | None = Field(default=None, gt=0)


class VentaCreate(BaseModel):
    canal: Literal["MAYORISTA", "DETAL"]
    cliente: str = Field(..., min_length=1, max_length=150)
    detalles: List[VentaDetalleCreate] = Field(..., min_length=1)


class PedidoDetalleCreate(BaseModel):
    sku_prenda: str = Field(..., min_length=1, max_length=50)
    cantidad: int = Field(..., gt=0)
    id_produccion: int = Field(..., gt=0)


class PedidoCreate(BaseModel):
    canal: Literal["MAYORISTA", "DETAL"]
    cliente: str = Field(..., min_length=1, max_length=150)
    detalles: List[PedidoDetalleCreate] = Field(..., min_length=1)


class PedidoResponse(BaseModel):
    id_venta: int
    canal: str
    cliente: str
    total: float
    mensaje: str


class TrasladoPrendaCreate(BaseModel):
    sku_prenda: str = Field(..., min_length=1, max_length=50)
    ubicacion_origen: Literal[
        "BODEGA_MAYORISTA", "BODEGA_LOCAL", "LOCAL"
    ]
    ubicacion_destino: Literal[
        "BODEGA_MAYORISTA", "BODEGA_LOCAL", "LOCAL"
    ]
    cantidad: int = Field(..., gt=0)
    id_produccion: int | None = Field(default=None, gt=0)


class InventarioInicialPrendaCreate(BaseModel):
    sku_prenda: str = Field(..., min_length=1, max_length=50)
    ubicacion: Literal[
        "BODEGA_MAYORISTA", "BODEGA_LOCAL", "LOCAL"
    ]
    cantidad: int = Field(..., gt=0)
    costo_unitario: float = Field(..., ge=0)


class ProductoPreciosUpdate(BaseModel):
    precio_mayorista: float = Field(..., gt=0)
    precio_detal: float = Field(..., gt=0)
    costo_mano_obra: float = Field(..., ge=0)
