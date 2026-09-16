from sqlalchemy.orm import Session
from backend.models.models import IngresoInsumos, MateriaPrima, FichaTecnicaInsumo

class InsumosRepository:

    @staticmethod
    def obtener_materia_prima(db: Session, id_mp: int):
        return db.query(MateriaPrima).filter(MateriaPrima.id_materiaPrima == id_mp).first()

    @staticmethod
    def registrar_ingreso(db: Session, ingreso_data: dict):
        nuevo_ingreso = IngresoInsumos(**ingreso_data)
        db.add(nuevo_ingreso)
        return nuevo_ingreso

    @staticmethod
    def obtener_ultimo_costo(db: Session, id_mp: int):
        return db.query(IngresoInsumos).filter_by(id_materiaPrima=id_mp).order_by(IngresoInsumos.id_entrante.desc()).first()

    @staticmethod
    def guardar_linea_ficha(db: Session, sku: str, id_mp: int, cantidad: float):
        nueva_linea = FichaTecnicaInsumo(
            sku_prenda=sku,
            id_materiaPrima=id_mp,
            cantidad_estimada=cantidad
        )
        db.add(nueva_linea)
        return nueva_linea