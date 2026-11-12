import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from backend.bootstrap import STANDARD_AREAS, STANDARD_ROLES, initialize_database
from backend.config import initialize_environment
from backend.models.models import Area, Rol


class DatabaseBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

    def tearDown(self):
        self.engine.dispose()

    def test_bootstrap_is_idempotent(self):
        initialize_database(self.engine)
        initialize_database(self.engine)

        with Session(self.engine) as db:
            roles = tuple(
                db.query(Rol.id_rol, Rol.nombre_rol)
                .order_by(Rol.id_rol)
                .all()
            )
            areas = tuple(
                name
                for (name,) in db.query(Area.nombre_area)
                .order_by(Area.id_area)
                .all()
            )

        self.assertEqual(roles, STANDARD_ROLES)
        self.assertEqual(areas, STANDARD_AREAS)

    def test_bootstrap_adds_stock_minimum_to_legacy_material_table(self):
        with self.engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE materia_prima ("
                "id_materia_prima INTEGER PRIMARY KEY, "
                "nombre VARCHAR(100) NOT NULL, "
                "stock_actual NUMERIC(10, 2) NOT NULL)"
            ))
            connection.execute(text(
                "INSERT INTO materia_prima "
                "(id_materia_prima, nombre, stock_actual) "
                "VALUES (1, 'Material existente', 8)"
            ))

        initialize_database(self.engine)

        columns = {
            column["name"]
            for column in inspect(self.engine).get_columns("materia_prima")
        }
        self.assertIn("stock_minimo", columns)
        with self.engine.connect() as connection:
            minimum = connection.execute(text(
                "SELECT stock_minimo FROM materia_prima "
                "WHERE id_materia_prima = 1"
            )).scalar_one()
        self.assertEqual(minimum, 0)

    def test_bootstrap_extends_existing_diagram_tables_without_losing_rows(self):
        with self.engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE usuario ("
                "id_usuario INTEGER PRIMARY KEY, "
                "nombre VARCHAR(100) NOT NULL, "
                "correo VARCHAR(100) NOT NULL, "
                "password VARCHAR(255) NOT NULL, "
                "id_rol INTEGER NOT NULL)"
            ))
            connection.execute(text(
                "INSERT INTO usuario "
                "(id_usuario, nombre, correo, password, id_rol) "
                "VALUES (7, 'Operaria', 'operaria@example.test', 'hash', 2)"
            ))
            connection.execute(text(
                "CREATE TABLE modelo ("
                "id_modelo INTEGER PRIMARY KEY, "
                "nombre_modelo VARCHAR(100) NOT NULL, descripcion TEXT)"
            ))
            connection.execute(text(
                "INSERT INTO modelo (id_modelo, nombre_modelo) "
                "VALUES (4, 'Modelo existente')"
            ))
            connection.execute(text(
                "CREATE TABLE produccion ("
                "id_produccion INTEGER PRIMARY KEY, "
                "id_modelo INTEGER NOT NULL, cantidad INTEGER NOT NULL, "
                "fecha_inicio DATETIME, estado_general VARCHAR(50))"
            ))
            connection.execute(text(
                "INSERT INTO produccion "
                "(id_produccion, id_modelo, cantidad, estado_general) "
                "VALUES (9, 4, 25, 'EN_PROCESO')"
            ))

        initialize_database(self.engine)

        with self.engine.connect() as connection:
            user = connection.execute(text(
                "SELECT nombre, correo, password, estado "
                "FROM usuario WHERE id_usuario = 7"
            )).one()
            order = connection.execute(text(
                "SELECT id_modelo, cantidad, id_area, id_ingreso_insumos, "
                "cantidad_entregada FROM produccion WHERE id_produccion = 9"
            )).one()

        self.assertEqual(
            user,
            ("Operaria", "operaria@example.test", "hash", "ACTIVO"),
        )
        self.assertEqual(order, (4, 25, None, None, 0))

    def test_bootstrap_adds_process_fields_to_legacy_production_stages(self):
        with self.engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE etapa_produccion ("
                "id_etapa INTEGER PRIMARY KEY, "
                "id_produccion INTEGER NOT NULL, "
                "id_area_anterior INTEGER, "
                "id_area_nueva INTEGER NOT NULL, "
                "id_usuario INTEGER NOT NULL, "
                "fecha_cambio DATETIME NOT NULL)"
            ))
            connection.execute(text(
                "INSERT INTO etapa_produccion "
                "(id_etapa, id_produccion, id_area_nueva, id_usuario, fecha_cambio) "
                "VALUES (1, 1, 1, 1, '2026-01-01 10:00:00')"
            ))

        initialize_database(self.engine)

        columns = {
            column["name"]
            for column in inspect(self.engine).get_columns("etapa_produccion")
        }
        self.assertIn("estado", columns)
        self.assertIn("observaciones", columns)
        with self.engine.connect() as connection:
            state = connection.execute(text(
                "SELECT estado FROM etapa_produccion WHERE id_etapa = 1"
            )).scalar_one()
        self.assertEqual(state, "COMPLETADO")

    def test_bootstrap_adds_nullable_production_links_to_legacy_sales_tables(self):
        with self.engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE detalle_venta ("
                "id_detalle INTEGER PRIMARY KEY, "
                "id_venta INTEGER NOT NULL, "
                "sku_prenda VARCHAR(50) NOT NULL)"
            ))
            connection.execute(text(
                "CREATE TABLE movimiento_prenda ("
                "id_movimiento INTEGER PRIMARY KEY, "
                "sku_prenda VARCHAR(50) NOT NULL)"
            ))

        initialize_database(self.engine)
        initialize_database(self.engine)

        for table_name in ("detalle_venta", "movimiento_prenda"):
            columns = {
                column["name"]
                for column in inspect(self.engine).get_columns(table_name)
            }
            self.assertIn("id_produccion", columns)
            foreign_keys = inspect(self.engine).get_foreign_keys(table_name)
            self.assertTrue(any(
                key.get("referred_table") == "produccion"
                and key.get("constrained_columns") == ["id_produccion"]
                for key in foreign_keys
            ))

    def test_importing_application_does_not_connect_or_create_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = os.path.join(directory, "not-created-on-import.db")
            environment = os.environ.copy()
            environment["DATABASE_URL"] = f"sqlite:///{database_path}"
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import backend.main",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(os.path.exists(database_path))

    def test_environment_secrets_are_created_once_and_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            environment = {}

            initialize_environment(env_file, environment)
            first_secret = environment["SECRET_KEY"]
            first_admin_token = environment["INITIAL_ADMIN_TOKEN"]
            self.assertGreaterEqual(len(first_secret.encode("utf-8")), 32)
            self.assertGreaterEqual(len(first_admin_token.encode("utf-8")), 32)
            self.assertIn("CORS_ALLOWED_ORIGINS=", env_file.read_text())
            self.assertEqual(environment["SMTP_HOST"], "smtp.gmail.com")
            self.assertEqual(environment["SMTP_PORT"], "587")
            self.assertEqual(environment["SMTP_USE_TLS"], "true")
            self.assertEqual(environment["SMTP_USE_SSL"], "false")
            self.assertEqual(
                environment["DATABASE_URL"],
                "mysql+pymysql://root:123456@localhost/yullita_creaciones",
            )
            self.assertEqual(environment["HOST"], "127.0.0.1")
            self.assertEqual(environment["PORT"], "8000")
            self.assertEqual(
                environment["VITE_API_URL"],
                "http://127.0.0.1:8000/api",
            )

            loaded_environment = {}
            initialize_environment(env_file, loaded_environment)
            self.assertEqual(loaded_environment["SECRET_KEY"], first_secret)
            self.assertEqual(
                loaded_environment["INITIAL_ADMIN_TOKEN"],
                first_admin_token,
            )

    def test_local_environment_file_overrides_smtp_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "SMTP_HOST=smtp.local.test\n"
                "SMTP_PORT=2525\n"
                "SMTP_USE_TLS=false\n"
                "SMTP_USE_SSL=true\n",
                encoding="utf-8",
            )
            environment = {}

            initialize_environment(env_file, environment)

            self.assertEqual(environment["SMTP_HOST"], "smtp.local.test")
            self.assertEqual(environment["SMTP_PORT"], "2525")
            self.assertEqual(environment["SMTP_USE_TLS"], "false")
            self.assertEqual(environment["SMTP_USE_SSL"], "true")

    def test_environment_file_fills_blank_process_smtp_values(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "SMTP_HOST=smtp.configured.test\n"
                "SMTP_USERNAME=mailer@example.test\n"
                "SMTP_PASSWORD=app-password\n"
                "SMTP_FROM_EMAIL=mailer@example.test\n",
                encoding="utf-8",
            )
            environment = {
                "SMTP_HOST": "",
                "SMTP_USERNAME": "",
                "SMTP_PASSWORD": "",
                "SMTP_FROM_EMAIL": "",
            }

            initialize_environment(env_file, environment)

            self.assertEqual(environment["SMTP_HOST"], "smtp.configured.test")
            self.assertEqual(environment["SMTP_USERNAME"], "mailer@example.test")
            self.assertEqual(environment["SMTP_PASSWORD"], "app-password")
            self.assertEqual(
                environment["SMTP_FROM_EMAIL"],
                "mailer@example.test",
            )

    def test_environment_file_does_not_override_nonblank_process_values(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "SMTP_HOST=smtp.file.test\n",
                encoding="utf-8",
            )
            environment = {"SMTP_HOST": "smtp.environment.test"}

            initialize_environment(env_file, environment)

            self.assertEqual(environment["SMTP_HOST"], "smtp.environment.test")


if __name__ == "__main__":
    unittest.main()
