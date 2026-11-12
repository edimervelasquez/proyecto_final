from sqlalchemy.orm import Session

from backend.models.models import Merma, Produccion, TipoMerma


class MermaRepository:

    @staticmethod
    def listar(db: Session, limite: int = 200):
        return (
            db.query(Merma, TipoMerma.descripcion_merma)
            .join(TipoMerma, TipoMerma.id_tipo_merma == Merma.id_tipo_merma)
            .order_by(Merma.id_merma.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def listar_tipos(db: Session):
        return (
            db.query(TipoMerma)
            .order_by(TipoMerma.descripcion_merma, TipoMerma.id_tipo_merma)
            .all()
        )

    @staticmethod
    def obtener_orden(db: Session, id_produccion: int):
        return (
            db.query(Produccion)
            .filter(Produccion.id_produccion == id_produccion)
            .first()
        )

    @staticmethod
    def obtener_tipo(db: Session, id_tipo_merma: int):
        return (
            db.query(TipoMerma)
            .filter(TipoMerma.id_tipo_merma == id_tipo_merma)
            .first()
        )

    @staticmethod
    def registrar(db: Session, data: dict):
        merma = Merma(**data)
        db.add(merma)
        return merma
