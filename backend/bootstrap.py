from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, engine
from backend.models.models import (
    Area,
    EtapaProduccion,
    FichaTecnicaInsumo,
    InventarioPrenda,
    MovimientoPrenda,
    OrdenComercial,
    Produccion,
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

    if "usuario" in tables:
        user_columns = {
            column["name"] for column in inspector.get_columns("usuario")
        }
        recovery_columns = {
            "correo_recuperacion": "VARCHAR(254) NULL",
            "codigo_recuperacion_hash": "VARCHAR(64) NULL",
            "codigo_recuperacion_expira": "INTEGER NULL",
            "intentos_codigo_recuperacion": "INTEGER NOT NULL DEFAULT 0",
        }
        for column_name, definition in recovery_columns.items():
            if column_name not in user_columns:
                with database_engine.begin() as connection:
                    connection.execute(text(
                        f"ALTER TABLE usuario ADD COLUMN "
                        f"{column_name} {definition}"
                    ))

    for table_name in ("detalle_venta", "movimiento_prenda"):
        columns = {
            column["name"]
            for column in inspector.get_columns(table_name)
        }
        foreign_keys = inspector.get_foreign_keys(table_name)
        has_production_fk = any(
            foreign_key.get("referred_table") == "produccion"
            and foreign_key.get("constrained_columns") == ["id_produccion"]
            for foreign_key in foreign_keys
        )
        if "id_produccion" not in columns:
            with database_engine.begin() as connection:
                if database_engine.dialect.name == "sqlite":
                    connection.execute(text(
                        f"ALTER TABLE {table_name} ADD COLUMN id_produccion "
                        "INTEGER REFERENCES produccion (id_produccion)"
                    ))
                elif database_engine.dialect.name == "mysql":
                    connection.execute(text(
                        f"ALTER TABLE {table_name} "
                        "ADD COLUMN id_produccion INTEGER NULL"
                    ))
                else:
                    raise RuntimeError(
                        "La migración de trazabilidad de pedidos solo está "
                        "implementada para SQLite y MySQL."
                    )
            inspector = inspect(database_engine)
            foreign_keys = inspector.get_foreign_keys(table_name)
            has_production_fk = any(
                foreign_key.get("referred_table") == "produccion"
                and foreign_key.get("constrained_columns") == ["id_produccion"]
                for foreign_key in foreign_keys
            )

        if not has_production_fk:
            if database_engine.dialect.name == "mysql":
                with database_engine.begin() as connection:
                    connection.execute(text(
                        f"ALTER TABLE {table_name} "
                        f"ADD CONSTRAINT fk_{table_name}_produccion "
                        "FOREIGN KEY (id_produccion) "
                        "REFERENCES produccion (id_produccion)"
                    ))
            elif database_engine.dialect.name == "sqlite":
                raise RuntimeError(
                    f"La tabla {table_name} ya tiene id_produccion pero no "
                    "la llave foránea a produccion. Migra esa tabla "
                    "manualmente antes de iniciar la aplicación."
                )

        inspector = inspect(database_engine)

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

    if "etapa_produccion" in tables:
        stage_columns = {
            column["name"]
            for column in inspector.get_columns("etapa_produccion")
        }
        with database_engine.begin() as connection:
            if "estado" not in stage_columns:
                connection.execute(
                    text(
                        "ALTER TABLE etapa_produccion "
                        "ADD COLUMN estado VARCHAR(30) "
                        "NOT NULL DEFAULT 'COMPLETADO'"
                    )
                )
            if "observaciones" not in stage_columns:
                connection.execute(
                    text(
                        "ALTER TABLE etapa_produccion "
                        "ADD COLUMN observaciones TEXT"
                    )
                )


def _ensure_diagram_schema_compatibility(database_engine: Engine):
    inspector = inspect(database_engine)
    tables = set(inspector.get_table_names())
    additions = {
        "usuario": {
            "cedula_usuario": "VARCHAR(20) NULL",
            "estado": "VARCHAR(20) NOT NULL DEFAULT 'ACTIVO'",
        },
        "produccion": {
            "id_area": "INTEGER NULL",
            "id_ingreso_insumos": "INTEGER NULL",
            "fecha_entrega": "DATE NULL",
            "cantidad_entregada": "INTEGER NOT NULL DEFAULT 0",
        },
    }

    for table_name, columns_to_add in additions.items():
        if table_name not in tables:
            continue
        existing_columns = {
            column["name"]
            for column in inspector.get_columns(table_name)
        }
        for column_name, definition in columns_to_add.items():
            if column_name in existing_columns:
                continue
            with database_engine.begin() as connection:
                connection.execute(text(
                    f"ALTER TABLE {table_name} "
                    f"ADD COLUMN {column_name} {definition}"
                ))
            inspector = inspect(database_engine)
            existing_columns.add(column_name)


def _ensure_product_sku_foreign_keys(database_engine: Engine):
    if database_engine.dialect.name != "mysql":
        return

    inspector = inspect(database_engine)
    for table_name in (
        "ficha_tecnica_insumo",
        "orden_comercial",
        "inventario_prenda",
        "movimiento_prenda",
    ):
        has_product_fk = any(
            foreign_key.get("referred_table") == "producto_comercial"
            and foreign_key.get("constrained_columns") == ["sku_prenda"]
            for foreign_key in inspector.get_foreign_keys(table_name)
        )
        if has_product_fk:
            continue

        with database_engine.connect() as connection:
            orphan_count = connection.execute(text(
                f"SELECT COUNT(*) FROM {table_name} child "
                "LEFT JOIN producto_comercial product "
                "ON product.sku_prenda = child.sku_prenda "
                "WHERE product.sku_prenda IS NULL"
            )).scalar_one()
        if orphan_count:
            raise RuntimeError(
                f"No se puede agregar la llave foranea de {table_name}. "
                f"Hay {orphan_count} SKU sin producto comercial asociado; "
                "corrige o registra esos productos y reinicia el backend."
            )

        with database_engine.begin() as connection:
            connection.execute(text(
                f"ALTER TABLE {table_name} "
                f"ADD CONSTRAINT fk_{table_name}_producto_sku "
                "FOREIGN KEY (sku_prenda) "
                "REFERENCES producto_comercial (sku_prenda)"
            ))
        inspector = inspect(database_engine)


def initialize_database(
    database_engine: Engine = engine,
):
    _ensure_diagram_schema_compatibility(database_engine)
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

        for order in db.query(Produccion).all():
            active_stage = (
                db.query(EtapaProduccion)
                .filter(
                    EtapaProduccion.id_produccion == order.id_produccion,
                    EtapaProduccion.id_area_nueva == order.id_area,
                )
                .order_by(EtapaProduccion.id_etapa.desc())
                .first()
            )
            if active_stage is not None:
                active_stage.estado = "EN_PROCESO"
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
        for model in (
            OrdenComercial,
            InventarioPrenda,
            MovimientoPrenda,
        ):
            for (sku,) in db.query(model.sku_prenda).distinct().all():
                if db.query(ProductoComercial).filter_by(
                    sku_prenda=sku
                ).first():
                    continue
                db.add(ProductoComercial(
                    sku_prenda=sku,
                    nombre_producto=sku,
                    descripcion="Producto legado vinculado a inventario o producción.",
                    costo_mano_obra=0,
                    precio_mayorista=0,
                    precio_detal=0,
                    activo=1,
                ))
        db.commit()

    _ensure_product_sku_foreign_keys(database_engine)
