from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

class IngresoInsumoCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id_materiaPrima": None,
                    "nombre_material": "Tela nueva",
                    "cantidad": 100,
                    "proveedor": "Proveedor de prueba",
                    "costo_unitario": 5000,
                    "fecha_ingreso": "2026-11-03",
                    "stock_minimo": 10,
                },
                {
                    "id_materiaPrima": 1,
                    "nombre_material": None,
                    "cantidad": 100,
                    "proveedor": "Proveedor de prueba",
                    "costo_unitario": 5000,
                    "fecha_ingreso": "2026-11-03",
                    "stock_minimo": 0,
                },
            ]
        }
    )

    id_materiaPrima: Optional[int] = Field(
        default=None,
        description=(
            "Para crear una materia prima nueva, deja este valor en null. "
            "Para un material existente, indica su ID y deja nombre_material "
            "en null."
        ),
    )
    nombre_material: Optional[str] = Field(
        default=None,
        max_length=100,
        description=(
            "Nombre del nuevo material. No lo envíes junto con "
            "id_materiaPrima."
        ),
    )
    cantidad: Decimal = Field(
        ..., gt=0, description="La cantidad debe ser mayor a cero"
    )
    proveedor: Optional[str] = "Proveedor Genérico"
    costo_unitario: Optional[float] = Field(default=0.0, ge=0)
    fecha_ingreso: Optional[date] = None
    stock_minimo: Decimal = Field(default=Decimal("0"), ge=0)


class IngresoInsumoResponse(BaseModel):
    mensaje: str
    id_ingreso: int
    id_materiaPrima: int
    nombre_material: str
    nuevo_stock: float


class StockMinimoUpdate(BaseModel):
    stock_minimo: Decimal = Field(..., ge=0)

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


class FichaTecnicaDetalleResponse(BaseModel):
    id_materiaPrima: int
    nombre_material: str
    cantidad: float
    costo_estimado: float


class FichaTecnicaResponse(BaseModel):
    mensaje: str
    sku_prenda: str
    costo_materiales: float
    costo_mano_obra: float
    costo_total_fabricacion: float
    precio_mayorista: float
    precio_detal: float
    detalles: List[FichaTecnicaDetalleResponse]