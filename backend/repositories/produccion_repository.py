from sqlalchemy.orm import Session

from backend.models.models import FichaTecnicaInsumo, MateriaPrima, Produccion


class ProduccionRepository:

    @staticmethod
    def obtener_insumos_receta(db: Session, sku_prenda: str):
        return (
            db.query(FichaTecnicaInsumo)
            .filter(FichaTecnicaInsumo.sku_prenda == sku_prenda)
            .all()
        )

    @staticmethod
    def obtener_materia_prima(db: Session, id_materia_prima: int):
        return (
            db.query(MateriaPrima)
            .filter(MateriaPrima.id_materiaPrima == id_materia_prima)
            .first()
        )

    @staticmethod
    def registrar_orden(db: Session, orden_data: dict):
        orden = Produccion(**orden_data)
        db.add(orden)
        return orden

    @staticmethod
    def obtener_actividad_reciente(db: Session, limite: int = 10):
        return (
            db.query(Produccion)
            .order_by(Produccion.id_produccion.desc())
            .limit(limite)
            .all()
        )
