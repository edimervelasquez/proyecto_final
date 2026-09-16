from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class IngresoInsumoCreate(BaseModel):
    id_materiaPrima: int
    cantidad: float = Field(..., gt=0, description="La cantidad debe ser mayor a cero")
    proveedor: Optional[str] = "Proveedor Genérico"
    costo_unitario: Optional[float] = 0.0
    fecha_ingreso: Optional[date] = None

class DetalleInsumoFicha(BaseModel):
    id_materiaPrima: int
    cantidad_estimada: float = Field(..., gt=0)

class FichaTecnicaCreate(BaseModel):
    sku_prenda: str
    insumos: List[DetalleInsumoFicha]
    costo_mano_obra: Optional[float] = 0.0