from sqlalchemy.orm import Session

from backend.schemas.merma_schema import MermaCreate
from backend.services.merma_service import MermaService


class MermaController:

    @staticmethod
    def listar(db: Session):
        return MermaService.listar(db)

    @staticmethod
    def listar_tipos(db: Session):
        return MermaService.listar_tipos(db)

    @staticmethod
    def registrar(data: MermaCreate, db: Session):
        return MermaService.registrar(data, db)
