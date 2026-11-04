from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class TrazoProduccionCreate(BaseModel):
    id_ingreso: int = Field(..., gt=0)
    sku_prenda: str = Field(..., min_length=1, max_length=50)
    cantidad_materia_prima: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    cantidad_prendas: int = Field(..., gt=0)
    observaciones: Optional[str] = Field(default=None, max_length=1000)


class TrazoProduccionResponse(BaseModel):
    id_trazo: int
    id_ingreso: int
    id_materiaPrima: int
    nombre_material: str
    sku_prenda: str
    id_produccion: Optional[int] = None
    cantidad_materia_prima: Decimal
    cantidad_prendas: int
    observaciones: Optional[str] = None
    id_usuario: int
    fecha_registro: datetime


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
    id_trazos: Optional[list[int]] = Field(
        default=None,
        min_length=1,
        description=(
            "Trazos que detallan el ingreso y la cantidad de cada materia prima "
            "usada. Si se envían, deben cubrir exactamente la ficha técnica."
        ),
    )
