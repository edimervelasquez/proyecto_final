import os
import unittest
from datetime import date, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.main import create_app
from backend.models.models import (
    Area,
    FichaTecnicaInsumo,
    IngresoInsumos,
    MateriaPrima,
    ProductoComercial,
    Usuario,
)
from backend.security import create_access_token

os.environ["SECRET_KEY"] = "unit-test-secret-key-at-least-32-bytes-long"


class ProductionSequenceApiTests(unittest.TestCase):
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
                empleado="Operario API",
                contrasenia="unused",
                correo="production-api@example.test",
                cedula_usuario="PRODUCTION-API",
                id_rol=1,
                estado="ACTIVO",
            )
            material = MateriaPrima(
                nombre_material="Tela para secuencia",
                Cantidad_materiaPrima=30,
            )
            product = ProductoComercial(
                sku_prenda="SEQUENCE-API",
                nombre_producto="Prenda de secuencia",
                costo_mano_obra=Decimal("2.00"),
                precio_mayorista=Decimal("12.00"),
                precio_detal=Decimal("20.00"),
                activo=1,
            )
            db.add_all((self.user, material, product))
            db.flush()
            db.add_all((
                IngresoInsumos(
                    id_materiaPrima=material.id_materiaPrima,
                    cantidad_materia_prima=30,
                    proveedor="Proveedor API",
                    costo_unitario=Decimal("5.00"),
                    fecha_ingreso=date.today(),
                ),
                FichaTecnicaInsumo(
                    sku_prenda=product.sku_prenda,
                    id_materiaPrima=material.id_materiaPrima,
                    cantidad_estimada=Decimal("1.00"),
                ),
            ))
            db.commit()
            self.user_id = self.user.id_usuario

        self.headers = {
            "Authorization": f"Bearer {create_access_token(self.user_id, 'ADMINISTRADOR')}"
        }

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.engine.dispose()

    def test_sequence_routes_are_tagged_and_expose_bearer_auth_in_openapi(self):
        openapi = self.client.get("/openapi.json").json()
        create_order = openapi["paths"]["/api/produccion/ordenes"]["post"]
        list_processes = openapi["paths"][
            "/api/produccion/ordenes/{id_produccion}/procesos"
        ]["get"]
        advance = openapi["paths"][
            "/api/produccion/ordenes/{id_produccion}/avanzar"
        ]["post"]

        self.assertEqual(create_order["tags"], ["Producción"])
        self.assertEqual(list_processes["tags"], ["Producción"])
        self.assertEqual(advance["tags"], ["Producción"])
        self.assertIn("security", create_order)
        self.assertIn("security", list_processes)
        self.assertIn("security", advance)

    def test_order_and_stage_progression_record_status_operator_and_observations(self):
        unauthenticated = self.client.get(
            "/api/produccion/ordenes/1/procesos"
        )
        self.assertEqual(unauthenticated.status_code, 401)

        corte = self.client.get(
            "/api/produccion/areas",
            headers=self.headers,
        ).json()
        corte_id = next(area["id_area"] for area in corte if area["nombre_area"] == "Corte")
        confeccion_id = next(
            area["id_area"]
            for area in corte
            if area["nombre_area"] == "Confección"
        )

        created = self.client.post(
            "/api/produccion/ordenes",
            headers=self.headers,
            json={
                "id_area": corte_id,
                "sku_prenda": "SEQUENCE-API",
                "cantidad_a_producir": 5,
                "fecha_entrega": (date.today() + timedelta(days=7)).isoformat(),
                "canal_destino": "DETAL",
                "observaciones": "Tela verificada al iniciar.",
            },
        )
        self.assertEqual(created.status_code, 201, created.text)
        order_id = created.json()["id_orden"]

        initial_history = self.client.get(
            f"/api/produccion/ordenes/{order_id}/procesos",
            headers=self.headers,
        )
        self.assertEqual(initial_history.status_code, 200)
        self.assertEqual(
            initial_history.json(),
            [{
                "id_etapa": initial_history.json()[0]["id_etapa"],
                "id_produccion": order_id,
                "id_area": corte_id,
                "etapa": "Corte",
                "estado": "EN_PROCESO",
                "fecha": initial_history.json()[0]["fecha"],
                "operario_id": self.user_id,
                "operario": "Operario API",
                "observaciones": "Tela verificada al iniciar.",
            }],
        )

        advanced = self.client.post(
            f"/api/produccion/ordenes/{order_id}/avanzar",
            headers=self.headers,
            json={
                "id_area_destino": confeccion_id,
                "observaciones": "Corte terminado y revisado.",
            },
        )
        self.assertEqual(advanced.status_code, 200, advanced.text)
        self.assertEqual(advanced.json()["etapa"], "Confección")
        self.assertEqual(advanced.json()["estado"], "EN_PROCESO")
        self.assertEqual(advanced.json()["operario_id"], self.user_id)

        history = self.client.get(
            f"/api/produccion/ordenes/{order_id}/procesos",
            headers=self.headers,
        ).json()
        self.assertEqual(
            [process["estado"] for process in history],
            ["COMPLETADO", "EN_PROCESO"],
        )
        self.assertEqual(
            history[0]["observaciones"],
            "Corte terminado y revisado.",
        )
        self.assertEqual(history[1]["etapa"], "Confección")


if __name__ == "__main__":
    unittest.main()
