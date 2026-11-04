from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.repositories.calidad_repository import CalidadRepository
from backend.repositories.trazabilidad_repository import TrazabilidadRepository
from backend.services.comercial_service import ComercialService
from backend.models.models import Area, EtapaProduccion


class CalidadService:

    @staticmethod
    def registrar_control(data, db: Session, id_usuario: int):
        orden = CalidadRepository.obtener_produccion(db, data.id_produccion)
        if not orden:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No se encontró ninguna orden de producción con el "
                    f"ID {data.id_produccion}."
                ),
            )

        cantidad_previa = CalidadRepository.obtener_total_reportado(
            db, data.id_produccion
        )
        total_procesado = (
            cantidad_previa + data.cantidad_optima + data.cantidad_defectuosa
        )
        if data.cantidad_optima + data.cantidad_defectuosa <= 0:
            raise HTTPException(
                status_code=400,
                detail="El control debe incluir al menos una unidad revisada.",
            )
        if total_procesado > orden.cantidad_recibida:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"El lote recibió {orden.cantidad_recibida} unidades y ya "
                    f"tiene {cantidad_previa} inspeccionadas. Este reporte "
                    "supera las unidades pendientes."
                ),
            )
        area = db.query(Area).filter(Area.id_area == orden.id_area).first()
        if not area or area.nombre_area != "Calidad y Empaque":
            raise HTTPException(
                status_code=409,
                detail="El control de calidad solo se registra en el área Calidad y Empaque.",
            )

        try:
            reporte = CalidadRepository.registrar_reporte(
                db,
                {
                    "id_produccion": data.id_produccion,
                    "id_usuario": id_usuario,
                    "cantidad_optima": data.cantidad_optima,
                    "cantidad_defectuosa": data.cantidad_defectuosa,
                    "observaciones": data.observaciones,
                },
            )
            ComercialService.registrar_aprobadas_de_orden(
                db, data.id_produccion, data.cantidad_optima, id_usuario
            )
            orden.cantidad_entregada = (orden.cantidad_entregada or 0) + data.cantidad_optima
            db.flush()
            nombre_orden = f"Control de calidad OP-{data.id_produccion}"
            TrazabilidadRepository.registrar(
                db,
                "control_calidad",
                reporte.id_control,
                nombre_orden,
                id_usuario,
                "Control de calidad",
                "Inspección registrada",
            )
            if cantidad_previa + data.cantidad_optima + data.cantidad_defectuosa == orden.cantidad_recibida:
                estado = "Finalizada"
                proceso = "Control de calidad"
                etapa_calidad = (
                    db.query(EtapaProduccion)
                    .filter(
                        EtapaProduccion.id_produccion == data.id_produccion,
                        EtapaProduccion.id_area_nueva == orden.id_area,
                        EtapaProduccion.estado == "EN_PROCESO",
                    )
                    .order_by(EtapaProduccion.id_etapa.desc())
                    .first()
                )
                if etapa_calidad:
                    etapa_calidad.estado = "COMPLETADO"
                    etapa_calidad.id_usuario = id_usuario
                    resumen_inspeccion = (
                        f"Inspección finalizada: {cantidad_previa + data.cantidad_optima} "
                        f"aprobadas y "
                        f"{cantidad_previa + data.cantidad_defectuosa} defectuosas."
                    )
                    etapa_calidad.observaciones = " ".join(
                        filter(
                            None,
                            (etapa_calidad.observaciones, resumen_inspeccion, data.observaciones),
                        )
                    )
            else:
                estado = "Inspección parcial"
                proceso = "Control de calidad"
            TrazabilidadRepository.actualizar_estado(
                db,
                "orden_produccion",
                data.id_produccion,
                estado,
                proceso,
                id_usuario,
            )
            db.commit()
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return {
            "mensaje": (
                f"¡Control de calidad para la Orden #{data.id_produccion} "
                "guardado exitosamente!"
            ),
            "unidades_aprobadas": data.cantidad_optima,
            "unidades_defectuosas": data.cantidad_defectuosa,
            "estado": estado,
        }

    @staticmethod
    def listar_controles(db: Session):
        resultado = []
        for control, orden, empleado in CalidadRepository.obtener_reportes(db):
            resultado.append({
                "id_control": control.id_control,
                "id_orden": orden.id_produccion,
                "cantidad_optima": control.cantidad_optima,
                "cantidad_defectuosa": control.cantidad_defectuosa,
                "observaciones": control.observaciones,
                "registrado_por": empleado,
                "fecha_registro": control.fecha_registro.isoformat()
                if control.fecha_registro
                else None,
                "proceso": "Control de calidad",
                "estado": "Inspección registrada",
            })
        return resultado

    @staticmethod
    def obtener_resumen(db: Session):
        cantidad_optima, cantidad_defectuosa = CalidadRepository.obtener_totales(db)
        inspeccionadas = cantidad_optima + cantidad_defectuosa
        return {
            "total_optimo": cantidad_optima,
            "total_defectuoso": cantidad_defectuosa,
            "aprobacion_calidad": round(
                cantidad_optima / inspeccionadas * 100, 1
            )
            if inspeccionadas
            else 0.0,
        }
