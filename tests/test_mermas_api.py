import os
import unittest
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.main import create_app
from backend.models.models import (
    Merma,
    Modelo,
    Produccion,
    TipoMerma,
    Trazabilidad,
    Usuario,
)
from backend.security import create_access_token


os.environ["SECRET_KEY"] = "unit-test-secret-key-at-least-32-bytes-long"


class MermasApiTests(unittest.TestCase):

    def setUp(self):
        os.environ["INITIAL_ADMIN_TOKEN"] = (
            "unit-test-initial-admin-token-at-least-32-bytes-long"
        )
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.client_context = TestClient(create_app(self.engine))
        self.client = self.client_context.__enter__()
        with Session(self.engine) as db:
            self.user = Usuario(
                empleado="Operario de mermas",
                contrasenia="unused",
                correo="mermas-api@example.test",
                cedula_usuario="MERMAS-API",
                id_rol=1,
                estado="ACTIVO",
            )
            tipo = TipoMerma(descripcion_merma="Tela sobrante")
            modelo = Modelo(nombre_modelo="Modelo de prueba")
            db.add_all((self.user, tipo, modelo))
            db.flush()
            orden = Produccion(
                id_modelo=modelo.id_modelo,
                cantidad_recibida=20,
            )
            db.add(orden)
            db.commit()
            self.user_id = self.user.id_usuario
            self.tipo_id = tipo.id_tipo_merma
            self.orden_id = orden.id_produccion
            self.headers = {
                "Authorization": (
                    f"Bearer {create_access_token(self.user_id, 'ADMINISTRADOR')}"
                )
            }

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.engine.dispose()

    def test_merma_routes_require_authentication_and_expose_contracts(self):
        self.assertEqual(self.client.get("/api/produccion/mermas").status_code, 401)
        self.assertEqual(
            self.client.get("/api/produccion/tipos-merma").status_code,
            401,
        )

        openapi = self.client.get("/openapi.json").json()
        merma_post = openapi["paths"]["/api/produccion/mermas"]["post"]
        self.assertEqual(merma_post["tags"], ["Mermas"])
        self.assertIn("security", merma_post)

    def test_lists_types_and_registers_a_production_waste_record(self):
        tipos = self.client.get(
            "/api/produccion/tipos-merma",
            headers=self.headers,
        )
        self.assertEqual(tipos.status_code, 200, tipos.text)
        self.assertEqual(
            tipos.json(),
            [{
                "id_tipo_merma": self.tipo_id,
                "descripcion_merma": "Tela sobrante",
            }],
        )

        created = self.client.post(
            "/api/produccion/mermas",
            headers=self.headers,
            json={
                "id_produccion": self.orden_id,
                "id_tipo_merma": self.tipo_id,
                "cantidad_sobrante": "2.50",
            },
        )
        self.assertEqual(created.status_code, 201, created.text)
        self.assertEqual(created.json()["id_produccion"], self.orden_id)
        self.assertEqual(created.json()["id_tipo_merma"], self.tipo_id)
        self.assertEqual(created.json()["descripcion_tipo_merma"], "Tela sobrante")
        self.assertEqual(created.json()["cantidad_sobrante"], "2.50")
        self.assertIsNotNone(created.json()["fecha_registro"])

        listed = self.client.get(
            "/api/produccion/mermas",
            headers=self.headers,
        )
        self.assertEqual(listed.status_code, 200, listed.text)
        self.assertEqual(len(listed.json()), 1)
        self.assertEqual(listed.json()[0]["id_merma"], created.json()["id_merma"])
        with Session(self.engine) as db:
            stored = db.query(Merma).one()
            self.assertEqual(stored.cantidad_sobrante, Decimal("2.50"))

    def test_registration_rejects_unknown_references_and_nonpositive_quantity(self):
        missing_order = self.client.post(
            "/api/produccion/mermas",
            headers=self.headers,
            json={
                "id_produccion": 9999,
                "id_tipo_merma": self.tipo_id,
                "cantidad_sobrante": "1.00",
            },
        )
        self.assertEqual(missing_order.status_code, 404)

        missing_type = self.client.post(
            "/api/produccion/mermas",
            headers=self.headers,
            json={
                "id_produccion": self.orden_id,
                "id_tipo_merma": 9999,
                "cantidad_sobrante": "1.00",
            },
        )
        self.assertEqual(missing_type.status_code, 404)

        invalid_quantity = self.client.post(
            "/api/produccion/mermas",
            headers=self.headers,
            json={
                "id_produccion": self.orden_id,
                "id_tipo_merma": self.tipo_id,
                "cantidad_sobrante": "0",
            },
        )
        self.assertEqual(invalid_quantity.status_code, 422)

    def test_registration_rejects_a_finalized_production_order(self):
        with Session(self.engine) as db:
            db.add(Trazabilidad(
                tipo_registro="orden_produccion",
                referencia=str(self.orden_id),
                nombre_registro=f"OP-{self.orden_id}",
                id_usuario=self.user_id,
                proceso="Control de calidad",
                estado="Finalizada",
            ))
            db.commit()

        response = self.client.post(
            "/api/produccion/mermas",
            headers=self.headers,
            json={
                "id_produccion": self.orden_id,
                "id_tipo_merma": self.tipo_id,
                "cantidad_sobrante": "1.00",
            },
        )
        self.assertEqual(response.status_code, 409)
