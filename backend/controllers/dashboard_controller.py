from sqlalchemy.orm import Session

from backend.services.comercial_service import ComercialService
from backend.services.dashboard_service import DashboardService


class DashboardController:

    @staticmethod
    def obtener_rendimiento(db: Session):
        return DashboardService.obtener_rendimiento(db)

    @staticmethod
    def obtener_resumen(db: Session):
        return DashboardService.obtener_resumen(db)

    @staticmethod
    def obtener_resumen_financiero(db: Session):
        return ComercialService.resumen_financiero(db)
