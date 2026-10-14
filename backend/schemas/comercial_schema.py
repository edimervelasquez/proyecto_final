from typing import Literal, List

from pydantic import BaseModel, Field


class VentaDetalleCreate(BaseModel):
    sku_prenda: str = Field(..., min_length=1, max_length=50)
    cantidad: int = Field(..., gt=0)


class VentaCreate(BaseModel):
    canal: Literal["MAYORISTA", "DETAL"]
    cliente: str = Field(..., min_length=1, max_length=150)
    detalles: List[VentaDetalleCreate] = Field(..., min_length=1)


class TrasladoPrendaCreate(BaseModel):
    sku_prenda: str = Field(..., min_length=1, max_length=50)
    ubicacion_origen: Literal[
        "BODEGA_MAYORISTA", "BODEGA_LOCAL", "LOCAL"
    ]
    ubicacion_destino: Literal[
        "BODEGA_MAYORISTA", "BODEGA_LOCAL", "LOCAL"
    ]
    cantidad: int = Field(..., gt=0)


class InventarioInicialPrendaCreate(BaseModel):
    sku_prenda: str = Field(..., min_length=1, max_length=50)
    ubicacion: Literal[
        "BODEGA_MAYORISTA", "BODEGA_LOCAL", "LOCAL"
    ]
    cantidad: int = Field(..., gt=0)
    costo_unitario: float = Field(..., ge=0)


class EtapaProduccionUpdate(BaseModel):
    id_area_destino: int


class ProductoPreciosUpdate(BaseModel):
    precio_mayorista: float = Field(..., gt=0)
    precio_detal: float = Field(..., gt=0)
    costo_mano_obra: float = Field(..., ge=0)
