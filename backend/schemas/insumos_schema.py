from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

class IngresoInsumoCreate(BaseModel):
    id_materiaPrima: Optional[int] = None
    nombre_material: Optional[str] = Field(default=None, max_length=100)
    cantidad: int = Field(..., gt=0, description="La cantidad debe ser mayor a cero")
    proveedor: Optional[str] = "Proveedor Genérico"
    costo_unitario: Optional[float] = Field(default=0.0, ge=0)
    fecha_ingreso: Optional[date] = None
    stock_minimo: int = Field(default=0, ge=0)


class StockMinimoUpdate(BaseModel):
    stock_minimo: int = Field(..., ge=0)

class DetalleInsumoFicha(BaseModel):
    id_materiaPrima: int
    cantidad_estimada: float = Field(..., gt=0)

class FichaTecnicaCreate(BaseModel):
    sku_prenda: str = Field(..., min_length=1, max_length=50)
    nombre_producto: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = None
    insumos: List[DetalleInsumoFicha] = Field(..., min_length=1)
    costo_mano_obra: Optional[float] = Field(default=0.0, ge=0)
    precio_mayorista: float = Field(..., gt=0)
    precio_detal: float = Field(..., gt=0)