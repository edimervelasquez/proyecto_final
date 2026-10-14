import os
import subprocess
import sys
import tempfile
import unittest

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from backend.bootstrap import STANDARD_AREAS, STANDARD_ROLES, initialize_database
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
                "id_materiaPrima INTEGER PRIMARY KEY, "
                "nombre_material VARCHAR(100) NOT NULL, "
                "Cantidad_materiaPrima INTEGER NOT NULL)"
            ))
            connection.execute(text(
                "INSERT INTO materia_prima "
                "(id_materiaPrima, nombre_material, Cantidad_materiaPrima) "
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
                "WHERE id_materiaPrima = 1"
            )).scalar_one()
        self.assertEqual(minimum, 0)

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


if __name__ == "__main__":
    unittest.main()
