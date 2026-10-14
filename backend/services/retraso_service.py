from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.repositories.produccion_repository import ProduccionRepository
from backend.repositories.trazabilidad_repository import TrazabilidadRepository
from backend.schemas.produccion_schema import RetrasoProduccionCreate
from backend.services.permisos_operativos import validar_usuario_operativo


class RetrasoService:

    @staticmethod
    def registrar_retraso(
        id_produccion: int,
        data: RetrasoProduccionCreate,
        db: Session,
        id_usuario: int,
    ):
        validar_usuario_operativo(db, id_usuario)
        orden = ProduccionRepository.obtener_orden_para_actualizar(
            db, id_produccion
        )
        if not orden:
            raise HTTPException(
                status_code=404,
                detail=f"No existe la orden OP-{id_produccion}.",
            )
        if (orden.cantidad_entregada or 0) >= orden.cantidad_recibida:
            raise HTTPException(
                status_code=400,
                detail="No se pueden registrar retrasos en una orden finalizada.",
            )
        if ProduccionRepository.obtener_retraso_abierto(db, id_produccion):
            raise HTTPException(
                status_code=409,
                detail="Esta orden ya tiene un retraso abierto.",
            )

        try:
            retraso = ProduccionRepository.registrar_retraso(
                db,
                {
                    "id_produccion": id_produccion,
                    "id_area": orden.id_area,
                    "id_usuario_inicio": id_usuario,
                    "motivo": data.motivo,
                    "detalle": (data.detalle or "").strip() or None,
                    "fecha_inicio": datetime.now(),
                },
            )
            db.flush()
            area = ProduccionRepository.obtener_area(db, orden.id_area)
            TrazabilidadRepository.actualizar_estado(
                db,
                "orden_produccion",
                id_produccion,
                "Retraso reportado",
                area.nombre_area if area else "Producción",
                id_usuario,
                crear_si_no_existe=True,
            )
            db.commit()
            return {
                "id_retraso": retraso.id_retraso,
                "mensaje": f"Se registró el retraso de la orden OP-{id_produccion}.",
                "estado": "Retraso reportado",
                "fecha_inicio": retraso.fecha_inicio.isoformat(),
            }
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def reanudar_produccion(
        id_retraso: int,
        db: Session,
        id_usuario: int,
    ):
        validar_usuario_operativo(db, id_usuario)
        retraso = ProduccionRepository.obtener_retraso_por_id(db, id_retraso)
        if not retraso:
            raise HTTPException(
                status_code=404,
                detail=f"No existe el registro de retraso #{id_retraso}.",
            )
        if retraso.fecha_fin:
            raise HTTPException(
                status_code=409,
                detail="Este retraso ya fue cerrado.",
            )
        orden = ProduccionRepository.obtener_orden_para_actualizar(
            db, retraso.id_produccion
        )
        if not orden:
            raise HTTPException(
                status_code=404,
                detail=f"No existe la orden OP-{retraso.id_produccion}.",
            )

        try:
            retraso.fecha_fin = datetime.now()
            retraso.id_usuario_reanuda = id_usuario
            area = ProduccionRepository.obtener_area(db, orden.id_area)
            TrazabilidadRepository.actualizar_estado(
                db,
                "orden_produccion",
                orden.id_produccion,
                "En producción",
                area.nombre_area if area else "Producción",
                id_usuario,
                crear_si_no_existe=True,
            )
            db.commit()
            minutos = int(
                (retraso.fecha_fin - retraso.fecha_inicio).total_seconds() // 60
            )
            return {
                "id_retraso": retraso.id_retraso,
                "mensaje": (
                    f"La orden OP-{orden.id_produccion} continúa en producción."
                ),
                "estado": "En producción",
                "minutos_detenida": minutos,
                "fecha_fin": retraso.fecha_fin.isoformat(),
            }
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def listar_retrasos(id_produccion: int, db: Session):
        if not ProduccionRepository.obtener_orden(db, id_produccion):
            raise HTTPException(
                status_code=404,
                detail=f"No existe la orden OP-{id_produccion}.",
            )
        return [
            RetrasoService._formatear_retraso(
                retraso,
                area,
                empleado,
                reanudado_por,
            )
            for retraso, area, empleado, reanudado_por
            in ProduccionRepository.obtener_retrasos(db, id_produccion)
        ]

    @staticmethod
    def listar_todos_retrasos(db: Session):
        return [
            RetrasoService._formatear_retraso(
                retraso,
                area,
                empleado,
                reanudado_por,
            )
            for retraso, area, empleado, reanudado_por
            in ProduccionRepository.obtener_todos_retrasos(db)
        ]

    @staticmethod
    def resumen_retrasos(db: Session):
        ahora = datetime.now()
        por_motivo = {}
        total_segundos = 0
        abiertos = 0
        for retraso, _, _, _ in ProduccionRepository.obtener_todos_retrasos(db):
            fin = retraso.fecha_fin or ahora
            segundos = max(
                0,
                int((fin - retraso.fecha_inicio).total_seconds()),
            )
            total_segundos += segundos
            if retraso.fecha_fin is None:
                abiertos += 1
            resumen_motivo = por_motivo.setdefault(
                retraso.motivo,
                {"motivo": retraso.motivo, "cantidad": 0, "minutos": 0},
            )
            resumen_motivo["cantidad"] += 1
            resumen_motivo["minutos"] += segundos // 60

        return {
            "retrasos_abiertos": abiertos,
            "tiempo_perdido_minutos": total_segundos // 60,
            "retrasos_por_motivo": sorted(
                por_motivo.values(),
                key=lambda registro: registro["minutos"],
                reverse=True,
            ),
            "retrasos_recientes": RetrasoService.listar_todos_retrasos(db)[:5],
        }

    @staticmethod
    def _formatear_retraso(
        retraso,
        area: str,
        empleado: str,
        reanudado_por: str,
    ):
        fin = retraso.fecha_fin or datetime.now()
        segundos = max(0, int((fin - retraso.fecha_inicio).total_seconds()))
        return {
            "id_retraso": retraso.id_retraso,
            "id_orden": retraso.id_produccion,
            "area": area,
            "motivo": retraso.motivo,
            "detalle": retraso.detalle,
            "registrado_por": empleado,
            "reanudado_por": reanudado_por,
            "fecha_inicio": retraso.fecha_inicio.isoformat(),
            "fecha_fin": retraso.fecha_fin.isoformat()
            if retraso.fecha_fin
            else None,
            "abierto": retraso.fecha_fin is None,
            "segundos_detenida": segundos,
            "minutos_detenida": segundos // 60,
        }
