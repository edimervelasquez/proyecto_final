from sqlalchemy.orm import Session

from backend.models.models import Produccion, ProgramacionUsuario


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
        reporte = ProgramacionUsuario(**reporte_data)
        db.add(reporte)
        return reporte
