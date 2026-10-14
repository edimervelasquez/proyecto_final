from sqlalchemy.orm import Session

from backend.models.models import IngresoInsumos, MateriaPrima, Produccion, Usuario


class DashboardRepository:

    @staticmethod
    def obtener_ordenes_produccion(db: Session):
        return db.query(Produccion).all()

    @staticmethod
    def obtener_materias_primas(db: Session):
        return db.query(MateriaPrima).all()

    @staticmethod
    def obtener_ingresos(db: Session):
        return db.query(IngresoInsumos).all()

    @staticmethod
    def contar_operarios_activos(db: Session):
        return (
            db.query(Usuario)
            .filter(Usuario.id_rol != 1)
            .filter(Usuario.estado.in_(["ACTIVO", "APROBADO"]))
            .count()
        )
