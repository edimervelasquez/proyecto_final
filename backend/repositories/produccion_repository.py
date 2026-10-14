from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased

from backend.models.models import (
    Area,
    FichaTecnicaInsumo,
    IngresoInsumos,
    MateriaPrima,
    Produccion,
    RetrasoProduccion,
    Usuario,
)


class ProduccionRepository:

    @staticmethod
    def obtener_insumos_receta(db: Session, sku_prenda: str):
        return (
            db.query(FichaTecnicaInsumo)
            .filter(FichaTecnicaInsumo.sku_prenda == sku_prenda)
            .all()
        )

    @staticmethod
    def obtener_materia_prima(
        db: Session, id_materia_prima: int, lock: bool = False
    ):
        query = db.query(MateriaPrima).filter(
            MateriaPrima.id_materiaPrima == id_materia_prima
        )
        return query.with_for_update().first() if lock else query.first()

    @staticmethod
    def registrar_orden(db: Session, orden_data: dict):
        orden = Produccion(**orden_data)
        db.add(orden)
        return orden

    @staticmethod
    def obtener_ultimo_ingreso(db: Session):
        return (
            db.query(IngresoInsumos)
            .order_by(IngresoInsumos.id_entrante.desc())
            .first()
        )

    @staticmethod
    def obtener_area(db: Session, id_area: int):
        return db.query(Area).filter(Area.id_area == id_area).first()

    @staticmethod
    def obtener_areas(db: Session):
        return db.query(Area).order_by(Area.nombre_area).all()

    @staticmethod
    def obtener_area_por_nombre(db: Session, nombre: str):
        return (
            db.query(Area)
            .filter(func.lower(Area.nombre_area) == nombre.lower())
            .first()
        )

    @staticmethod
    def crear_area(db: Session, nombre: str):
        area = Area(nombre_area=nombre)
        db.add(area)
        return area

    @staticmethod
    def obtener_ordenes(db: Session, limite: int = 100):
        return (
            db.query(Produccion)
            .order_by(Produccion.id_produccion.desc())
            .limit(limite)
            .all()
        )

    @staticmethod
    def obtener_orden_para_actualizar(db: Session, id_produccion: int):
        return (
            db.query(Produccion)
            .filter(Produccion.id_produccion == id_produccion)
            .with_for_update()
            .first()
        )

    @staticmethod
    def obtener_orden(db: Session, id_produccion: int):
        return (
            db.query(Produccion)
            .filter(Produccion.id_produccion == id_produccion)
            .first()
        )

    @staticmethod
    def obtener_retraso_abierto(db: Session, id_produccion: int):
        return (
            db.query(RetrasoProduccion)
            .filter(
                RetrasoProduccion.id_produccion == id_produccion,
                RetrasoProduccion.fecha_fin.is_(None),
            )
            .first()
        )

    @staticmethod
    def registrar_retraso(db: Session, retraso_data: dict):
        retraso = RetrasoProduccion(**retraso_data)
        db.add(retraso)
        return retraso

    @staticmethod
    def obtener_retrasos(db: Session, id_produccion: int):
        usuario_reanuda = aliased(Usuario)
        return (
            db.query(
                RetrasoProduccion,
                Area.nombre_area,
                Usuario.empleado,
                usuario_reanuda.empleado,
            )
            .join(Area, Area.id_area == RetrasoProduccion.id_area)
            .join(
                Usuario,
                Usuario.id_usuario == RetrasoProduccion.id_usuario_inicio,
            )
            .outerjoin(
                usuario_reanuda,
                usuario_reanuda.id_usuario == RetrasoProduccion.id_usuario_reanuda,
            )
            .filter(RetrasoProduccion.id_produccion == id_produccion)
            .order_by(RetrasoProduccion.fecha_inicio.desc())
            .all()
        )

    @staticmethod
    def obtener_todos_retrasos(db: Session):
        usuario_reanuda = aliased(Usuario)
        return (
            db.query(
                RetrasoProduccion,
                Area.nombre_area,
                Usuario.empleado,
                usuario_reanuda.empleado,
            )
            .join(Area, Area.id_area == RetrasoProduccion.id_area)
            .join(
                Usuario,
                Usuario.id_usuario == RetrasoProduccion.id_usuario_inicio,
            )
            .outerjoin(
                usuario_reanuda,
                usuario_reanuda.id_usuario == RetrasoProduccion.id_usuario_reanuda,
            )
            .order_by(RetrasoProduccion.fecha_inicio.desc())
            .all()
        )

    @staticmethod
    def obtener_retrasos_abiertos(db: Session):
        return (
            db.query(RetrasoProduccion)
            .filter(RetrasoProduccion.fecha_fin.is_(None))
            .all()
        )

    @staticmethod
    def obtener_retraso_por_id(db: Session, id_retraso: int):
        return (
            db.query(RetrasoProduccion)
            .filter(RetrasoProduccion.id_retraso == id_retraso)
            .with_for_update()
            .first()
        )

    @staticmethod
    def obtener_usuario(db: Session, id_usuario: int):
        return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    @staticmethod
    def obtener_actividad_reciente(db: Session, limite: int = 10):
        return (
            db.query(Produccion)
            .order_by(Produccion.id_produccion.desc())
            .limit(limite)
            .all()
        )
