from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.controllers.merma_controller import MermaController
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.schemas.merma_schema import MermaCreate, MermaRead, TipoMermaRead


router = APIRouter(
    prefix="/produccion",
    tags=["Mermas"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/mermas", response_model=list[MermaRead])
def listar_mermas(db: Session = Depends(get_db)):
    return MermaController.listar(db)


@router.get("/tipos-merma", response_model=list[TipoMermaRead])
def listar_tipos_merma(db: Session = Depends(get_db)):
    return MermaController.listar_tipos(db)


@router.post(
    "/mermas",
    status_code=status.HTTP_201_CREATED,
    response_model=MermaRead,
)
def registrar_merma(
    data: MermaCreate,
    db: Session = Depends(get_db),
):
    return MermaController.registrar(data, db)
