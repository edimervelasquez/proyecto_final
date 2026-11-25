from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class ProcesoProduccionCreate(BaseModel):
    id_area_destino: int = Field(..., gt=0)
    observaciones: Optional[str] = Field(default=None, max_length=1000)


class ProcesoProduccionResponse(BaseModel):
    id_etapa: int
    id_produccion: int
    id_area: int
    etapa: str
    estado: Literal["EN_PROCESO", "COMPLETADO"]
    fecha: datetime
    operario_id: int
    operario: str
    observaciones: Optional[str] = None


class AvanceProcesoResponse(ProcesoProduccionResponse):
    mensaje: str


class OrdenProduccionResponse(BaseModel):
    mensaje: str
    id_orden: int
    estado: str
    sku_prenda: str
    cantidad: int
    etapa_inicial: str
    fecha_entrega: date


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
    observaciones: Optional[str] = Field(default=None, max_length=1000)
