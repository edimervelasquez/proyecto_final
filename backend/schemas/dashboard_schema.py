from pydantic import BaseModel


class RendimientoResponse(BaseModel):
    total_recibido: int
    total_optimo: int
    total_defectuoso: int
    eficiencia: float
    precio_unitario: int
    total_monetario: int
