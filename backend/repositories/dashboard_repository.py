from sqlalchemy.orm import Session

from backend.models.models import Produccion


class DashboardRepository:

    @staticmethod
    def obtener_ordenes_produccion(db: Session):
        return db.query(Produccion).all()
