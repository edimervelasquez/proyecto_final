from sqlalchemy.orm import Session

from backend.schemas.comercial_schema import EtapaProduccionUpdate
from backend.schemas.produccion_schema import (
    AreaCreate,
    OrdenProduccionCreate,
    RetrasoProduccionCreate,
)
from backend.services.produccion_service import ProduccionService
from backend.services.retraso_service import RetrasoService


class ProduccionController:

    @staticmethod
    def registrar_orden(
        data: OrdenProduccionCreate,
        db: Session,
        id_usuario: int,
    ):
        return ProduccionService.registrar_orden(data, db, id_usuario)

    @staticmethod
    def actividad_reciente(db: Session):
        return ProduccionService.obtener_actividad_reciente(db)

    @staticmethod
    def listar_ordenes(db: Session):
        return ProduccionService.listar_ordenes(db)

    @staticmethod
    def listar_areas(db: Session):
        return ProduccionService.listar_areas(db)

    @staticmethod
    def crear_area(data: AreaCreate, db: Session):
        return ProduccionService.crear_area(data, db)

    @staticmethod
    def avanzar_etapa(
        id_produccion: int,
        data: EtapaProduccionUpdate,
        db: Session,
        id_usuario: int,
    ):
        return ProduccionService.avanzar_etapa(
            id_produccion,
            data.id_area_destino,
            db,
            id_usuario,
        )

    @staticmethod
    def listar_retrasos(db: Session):
        return RetrasoService.listar_todos_retrasos(db)

    @staticmethod
    def listar_retrasos_orden(id_produccion: int, db: Session):
        return RetrasoService.listar_retrasos(id_produccion, db)

    @staticmethod
    def registrar_retraso(
        id_produccion: int,
        data: RetrasoProduccionCreate,
        db: Session,
        id_usuario: int,
    ):
        return RetrasoService.registrar_retraso(
            id_produccion,
            data,
            db,
            id_usuario,
        )

    @staticmethod
    def reanudar_produccion(
        id_retraso: int,
        db: Session,
        id_usuario: int,
    ):
        return RetrasoService.reanudar_produccion(
            id_retraso,
            db,
            id_usuario,
        )
