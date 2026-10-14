from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class AreaCreate(BaseModel):
    nombre_area: str = Field(..., min_length=1, max_length=50)


class RetrasoProduccionCreate(BaseModel):
    motivo: Literal[
        "Reparación de prendas con defecto",
        "Falta de materia prima",
        "Falla de maquinaria",
        "Espera de instrucciones o aprobación",
        "Otro",
    ]
    detalle: Optional[str] = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validar_detalle_otro(self):
        if self.motivo == "Otro" and not (self.detalle or "").strip():
            raise ValueError("Especifica el motivo cuando seleccionas 'Otro'.")
        return self


class OrdenProduccionCreate(BaseModel):
    id_area: int
    sku_prenda: str
    cantidad_a_producir: int = Field(..., gt=0)
    fecha_entrega: date
    canal_destino: Literal["MAYORISTA", "DETAL"]
