from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.controllers.dashboard_controller import DashboardController
from backend.database import get_db
from backend.schemas.dashboard_schema import RendimientoResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/rendimiento", response_model=RendimientoResponse)
def obtener_rendimiento(db: Session = Depends(get_db)):
    return DashboardController.obtener_rendimiento(db)
