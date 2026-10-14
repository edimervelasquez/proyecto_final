from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, engine
from backend.models.models import (
    Area,
    FichaTecnicaInsumo,
    ProductoComercial,
    Rol,
    Trazabilidad,
)


STANDARD_ROLES = (
    (1, "ADMINISTRADOR"),
    (2, "TRABAJADOR"),
    (3, "VENDEDOR"),
)
STANDARD_AREAS = ("Corte", "Confección", "Estampado", "Calidad y Empaque")


def _ensure_schema_compatibility(database_engine: Engine):
    inspector = inspect(database_engine)
    tables = set(inspector.get_table_names())

    if "stock_minimo" not in {
        column["name"]
        for column in inspector.get_columns("materia_prima")
    }:
        with database_engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE materia_prima "
                    "ADD COLUMN stock_minimo INTEGER NOT NULL DEFAULT 0"
                )
            )

    if "descripcion" not in {
        column["name"]
        for column in inspector.get_columns("trazabilidad")
    }:
        with database_engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE trazabilidad ADD COLUMN descripcion TEXT")
            )

    if "inventario_prenda" in tables and "costo_promedio" not in {
        column["name"]
        for column in inspector.get_columns("inventario_prenda")
    }:
        with database_engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE inventario_prenda "
                    "ADD COLUMN costo_promedio NUMERIC(12, 2) NOT NULL DEFAULT 0"
                )
            )


def initialize_database(
    database_engine: Engine = engine,
):
    Base.metadata.create_all(bind=database_engine)
    _ensure_schema_compatibility(database_engine)

    with sessionmaker(bind=database_engine)() as db:
        for role_id, role_name in STANDARD_ROLES:
            role = db.query(Rol).filter(Rol.id_rol == role_id).first()
            if role is None:
                db.add(Rol(id_rol=role_id, nombre_rol=role_name))
            elif role.nombre_rol != role_name:
                role.nombre_rol = role_name

        for area_name in STANDARD_AREAS:
            area = db.query(Area).filter(Area.nombre_area == area_name).first()
            if area is None:
                db.add(Area(nombre_area=area_name))
        db.commit()

        skus = {
            sku
            for (sku,) in db.query(FichaTecnicaInsumo.sku_prenda).distinct().all()
        }
        for sku in skus:
            if db.query(ProductoComercial).filter_by(sku_prenda=sku).first():
                continue
            registro = db.query(Trazabilidad).filter_by(
                tipo_registro="ficha_tecnica",
                referencia=sku,
            ).first()
            db.add(ProductoComercial(
                sku_prenda=sku,
                nombre_producto=registro.nombre_registro if registro else sku,
                descripcion=registro.descripcion if registro else None,
                costo_mano_obra=0,
                precio_mayorista=0,
                precio_detal=0,
                activo=1,
            ))
        db.commit()
