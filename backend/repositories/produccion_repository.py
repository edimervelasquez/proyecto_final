from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased

from backend.models.models import (
    Area,
    EtapaProduccion,
    FichaTecnicaInsumo,
    IngresoInsumos,
    MateriaPrima,
    Modelo,
    Produccion,
    RetrasoProduccion,
    TrazoProduccion,
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
    def obtener_o_crear_modelo(db: Session, nombre: str, descripcion: str | None):
        modelo = (
            db.query(Modelo)
            .filter(func.lower(Modelo.nombre_modelo) == nombre.lower())
            .first()
        )
        if modelo is None:
            modelo = Modelo(nombre_modelo=nombre, descripcion=descripcion)
            db.add(modelo)
            db.flush()
        return modelo

    @staticmethod
    def obtener_ultimo_ingreso(db: Session):
        return (
            db.query(IngresoInsumos)
            .order_by(IngresoInsumos.id_entrante.desc())
            .first()
        )

    @staticmethod
    def obtener_ingreso(db: Session, id_ingreso: int, lock: bool = False):
        query = db.query(IngresoInsumos).filter(
            IngresoInsumos.id_entrante == id_ingreso
        )
        return query.with_for_update().first() if lock else query.first()

    @staticmethod
    def obtener_trazo(db: Session, id_trazo: int, lock: bool = False):
        query = db.query(TrazoProduccion).filter(
            TrazoProduccion.id_trazo == id_trazo
        )
        return query.with_for_update().first() if lock else query.first()

    @staticmethod
    def obtener_trazos_por_ids(db: Session, ids_trazos: list[int], lock: bool = False):
        query = db.query(TrazoProduccion).filter(
            TrazoProduccion.id_trazo.in_(ids_trazos)
        )
        return query.with_for_update().all() if lock else query.all()

    @staticmethod
    def registrar_trazo(db: Session, data: dict):
        trazo = TrazoProduccion(**data)
        db.add(trazo)
        return trazo

    @staticmethod
    def trazos_por_ingreso(db: Session, id_ingreso: int):
        return (
            db.query(TrazoProduccion)
            .filter(TrazoProduccion.id_ingreso == id_ingreso)
            .all()
        )

    @staticmethod
    def trazos_pendientes_por_material(db: Session, id_materia_prima: int):
        return (
            db.query(TrazoProduccion)
            .join(
                IngresoInsumos,
                IngresoInsumos.id_entrante == TrazoProduccion.id_ingreso,
            )
            .filter(
                IngresoInsumos.id_materiaPrima == id_materia_prima,
                TrazoProduccion.id_produccion.is_(None),
            )
            .all()
        )

    @staticmethod
    def listar_trazos(db: Session, limite: int = 100):
        return (
            db.query(
                TrazoProduccion,
                IngresoInsumos.id_materiaPrima,
                MateriaPrima.nombre_material,
            )
            .join(
                IngresoInsumos,
                IngresoInsumos.id_entrante == TrazoProduccion.id_ingreso,
            )
            .join(
                MateriaPrima,
                MateriaPrima.id_materiaPrima == IngresoInsumos.id_materiaPrima,
            )
            .order_by(TrazoProduccion.id_trazo.desc())
            .limit(limite)
            .all()
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
    def obtener_procesos(db: Session, id_produccion: int):
        return (
            db.query(EtapaProduccion, Area.nombre_area, Usuario.empleado)
            .join(Area, Area.id_area == EtapaProduccion.id_area_nueva)
            .join(Usuario, Usuario.id_usuario == EtapaProduccion.id_usuario)
            .filter(EtapaProduccion.id_produccion == id_produccion)
            .order_by(EtapaProduccion.id_etapa)
            .all()
        )

    @staticmethod
    def obtener_etapa_activa(db: Session, id_produccion: int):
        return (
            db.query(EtapaProduccion)
            .filter(
                EtapaProduccion.id_produccion == id_produccion,
                EtapaProduccion.estado == "EN_PROCESO",
            )
            .order_by(EtapaProduccion.id_etapa.desc())
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
