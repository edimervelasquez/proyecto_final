from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.repositories.calidad_repository import CalidadRepository


class CalidadService:

    @staticmethod
    def registrar_control(data, db: Session):
        orden = CalidadRepository.obtener_produccion(db, data.id_produccion)
        if not orden:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No se encontró ninguna orden de producción con el "
                    f"ID {data.id_produccion}."
                ),
            )

        total_procesado = data.cantidad_optima + data.cantidad_defectuosa
        if total_procesado > orden.cantidad_recibida:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Inconsistencia: El lote recibió {orden.cantidad_recibida} "
                    f"unidades, intentas reportar {total_procesado}."
                ),
            )

        try:
            orden.cantidad_entregada = data.cantidad_optima
            CalidadRepository.registrar_reporte(
                db,
                {
                    "id_programacion": 1,
                    "id_rol": 3,
                    "cantidad_recibida": orden.cantidad_recibida,
                    "cantidad_entregada": data.cantidad_optima,
                    "cantidad_defectuosa": data.cantidad_defectuosa,
                },
            )
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return {
            "mensaje": (
                f"¡Control de calidad para la Orden #{data.id_produccion} "
                "guardado exitosamente!"
            ),
            "unidades_aprobadas": data.cantidad_optima,
            "unidades_defectuosas": data.cantidad_defectuosa,
            "estado": "Lote cerrado y listo para distribución.",
        }
