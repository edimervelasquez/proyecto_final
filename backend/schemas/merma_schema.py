from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TipoMermaCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    descripcion_merma: str = Field(..., min_length=1, max_length=100)


class TipoMermaRead(BaseModel):
    id_tipo_merma: int
    descripcion_merma: str

    model_config = ConfigDict(from_attributes=True)


class MermaCreate(BaseModel):
    id_produccion: int = Field(..., gt=0)
    id_tipo_merma: int = Field(..., gt=0)
    cantidad_sobrante: Decimal = Field(
        ..., gt=0, max_digits=10, decimal_places=2
    )


class MermaRead(BaseModel):
    id_merma: int
    id_produccion: int
    id_tipo_merma: int
    descripcion_tipo_merma: str
    cantidad_sobrante: Decimal
    fecha_registro: datetime | None = None
