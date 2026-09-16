from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class OrdenProduccionCreate(BaseModel):
    id_area: int
    sku_prenda: str
    cantidad_a_producir: int = Field(..., gt=0)
    fecha_entrega: date
    id_usuario: Optional[int] = None
    id_empleado: Optional[int] = None
