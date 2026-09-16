from sqlalchemy.orm import Session

from backend.services.dashboard_service import DashboardService


class DashboardController:

    @staticmethod
    def obtener_rendimiento(db: Session):
        return DashboardService.obtener_rendimiento(db)
