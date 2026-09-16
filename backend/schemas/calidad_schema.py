from pydantic import BaseModel, Field


class ControlCalidadCreate(BaseModel):
    id_produccion: int
    cantidad_optima: int = Field(..., ge=0)
    cantidad_defectuosa: int = Field(..., ge=0)
