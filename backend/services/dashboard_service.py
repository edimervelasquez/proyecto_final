from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    @staticmethod
    def obtener_rendimiento(db: Session):
        try:
            ordenes = DashboardRepository.obtener_ordenes_produccion(db)
            total_recibido = sum(o.cantidad_recibida for o in ordenes)
            total_optimo = sum(o.cantidad_entregada or 0 for o in ordenes)
            total_defectuoso = sum(
                (o.cantidad_recibida - o.cantidad_entregada)
                for o in ordenes
                if o.cantidad_entregada is not None and o.cantidad_entregada > 0
            )
            precio_unitario = 35000
            eficiencia = (
                round((total_optimo / total_recibido) * 100, 1)
                if total_recibido > 0
                else 100.0
            )
            return {
                "total_recibido": total_recibido,
                "total_optimo": total_optimo,
                "total_defectuoso": total_defectuoso,
                "eficiencia": eficiencia,
                "precio_unitario": precio_unitario,
                "total_monetario": total_optimo * precio_unitario,
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
