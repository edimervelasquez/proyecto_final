from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.models.models import (
    FichaTecnicaInsumo,
    IngresoInsumos,
    MateriaPrima,
    MovimientoInsumo,
    Usuario,
)

class InsumosRepository:

    @staticmethod
    def obtener_materia_prima(db: Session, id_mp: int, lock: bool = False):
        query = db.query(MateriaPrima).filter(
            MateriaPrima.id_materiaPrima == id_mp
        )
        return query.with_for_update().first() if lock else query.first()

    @staticmethod
    def obtener_materia_por_nombre(db: Session, nombre: str):
        return (
            db.query(MateriaPrima)
            .filter(func.lower(MateriaPrima.nombre_material) == nombre.lower())
            .first()
        )

    @staticmethod
    def registrar_ingreso(db: Session, ingreso_data: dict):
        nuevo_ingreso = IngresoInsumos(**ingreso_data)
        db.add(nuevo_ingreso)
        return nuevo_ingreso

    @staticmethod
    def obtener_ultimo_costo(db: Session, id_mp: int):
        return db.query(IngresoInsumos).filter_by(id_materiaPrima=id_mp).order_by(IngresoInsumos.id_entrante.desc()).first()

    @staticmethod
    def obtener_costo_unitario_actual(db: Session, id_mp: int):
        ingreso = InsumosRepository.obtener_ultimo_costo(db, id_mp)
        return float(ingreso.costo_unitario or 0) if ingreso else 0.0

    @staticmethod
    def obtener_ingresos(db: Session, limite: int = 100):
        return (
            db.query(IngresoInsumos)
            .order_by(IngresoInsumos.id_entrante.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def obtener_materias_primas(db: Session):
        return db.query(MateriaPrima).order_by(MateriaPrima.nombre_material).all()

    @staticmethod
    def actualizar_stock_minimo(db: Session, id_mp: int, stock_minimo: int):
        material = InsumosRepository.obtener_materia_prima(db, id_mp, lock=True)
        if material:
            material.stock_minimo = stock_minimo
        return material

    @staticmethod
    def registrar_movimiento(db: Session, data: dict):
        movimiento = MovimientoInsumo(**data)
        db.add(movimiento)
        return movimiento

    @staticmethod
    def obtener_movimientos(db: Session, limite: int = 300):
        return (
            db.query(
                MovimientoInsumo,
                MateriaPrima.nombre_material,
                Usuario.empleado,
            )
            .join(
                MateriaPrima,
                MateriaPrima.id_materiaPrima
                == MovimientoInsumo.id_materiaPrima,
            )
            .join(
                Usuario,
                Usuario.id_usuario == MovimientoInsumo.id_usuario,
            )
            .order_by(
                MovimientoInsumo.fecha_movimiento.desc(),
                MovimientoInsumo.id_movimiento.desc(),
            )
            .limit(limite)
            .all()
        )

    @staticmethod
    def obtener_lineas_ficha(db: Session):
        return (
            db.query(FichaTecnicaInsumo)
            .order_by(FichaTecnicaInsumo.id_ficha)
            .all()
        )

    @staticmethod
    def existe_ficha(db: Session, sku: str):
        return (
            db.query(FichaTecnicaInsumo.id_ficha)
            .filter(FichaTecnicaInsumo.sku_prenda == sku)
            .first()
            is not None
        )

    @staticmethod
    def guardar_linea_ficha(db: Session, sku: str, id_mp: int, cantidad: float):
        nueva_linea = FichaTecnicaInsumo(
            sku_prenda=sku,
            id_materiaPrima=id_mp,
            cantidad_estimada=cantidad
        )
        db.add(nueva_linea)
        return nueva_linea