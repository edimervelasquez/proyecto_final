from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.models import ControlCalidad, OrdenComercial, Produccion, Usuario


class CalidadRepository:

    @staticmethod
    def obtener_produccion(db: Session, id_produccion: int):
        return (
            db.query(Produccion)
            .filter(Produccion.id_produccion == id_produccion)
            .first()
        )

    @staticmethod
    def registrar_reporte(db: Session, reporte_data: dict):
        reporte = ControlCalidad(**reporte_data)
        db.add(reporte)
        return reporte

    @staticmethod
    def obtener_total_reportado(db: Session, id_produccion: int):
        reportes = (
            db.query(ControlCalidad)
            .filter(ControlCalidad.id_produccion == id_produccion)
            .all()
        )
        return sum(
            reporte.cantidad_optima + reporte.cantidad_defectuosa
            for reporte in reportes
        )

    @staticmethod
    def obtener_reportes(db: Session, limite: int = 100):
        return (
            db.query(ControlCalidad, Produccion, Usuario.empleado)
            .join(Produccion, Produccion.id_produccion == ControlCalidad.id_produccion)
            .join(Usuario, Usuario.id_usuario == ControlCalidad.id_usuario)
            .order_by(ControlCalidad.id_control.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def obtener_totales(db: Session):
        fila = (
            db.query(
                func.coalesce(func.sum(ControlCalidad.cantidad_optima), 0),
                func.coalesce(func.sum(ControlCalidad.cantidad_defectuosa), 0),
            )
            .one()
        )
        return int(fila[0]), int(fila[1])

    @staticmethod
    def obtener_perdida_estimada(db: Session):
        return (
            db.query(
                func.coalesce(
                    func.sum(
                        ControlCalidad.cantidad_defectuosa
                        * OrdenComercial.costo_unitario_estimado
                    ),
                    0,
                )
            )
            .join(
                OrdenComercial,
                OrdenComercial.id_produccion == ControlCalidad.id_produccion,
            )
            .scalar()
        )
