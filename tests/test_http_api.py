import unittest
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.main import create_app
from backend.models.models import MateriaPrima, ProductoComercial, Rol, Usuario
from backend.security import create_access_token


class HttpApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.app = create_app(self.engine)
        self.client_context = TestClient(self.app)
        self.client = self.client_context.__enter__()

        with Session(self.engine) as db:
            role = db.query(Rol).filter_by(id_rol=1).one()
            user = Usuario(
                id_usuario=1,
                empleado="Admin HTTP",
                contrasenia="hash",
                correo="admin-http@example.test",
                cedula_usuario="HTTP-ADMIN",
                id_rol=1,
                estado="ACTIVO",
            )
            material = MateriaPrima(
                id_materiaPrima=1,
                nombre_material="Tela HTTP",
                Cantidad_materiaPrima=2,
                stock_minimo=0,
            )
            db.add_all((user, material, ProductoComercial(
                sku_prenda="HTTP-TEST-001",
                nombre_producto="Producto para prueba HTTP",
                descripcion="Registro exclusivo de pruebas",
                costo_mano_obra=Decimal("2000.00"),
                precio_mayorista=Decimal("12000.00"),
                precio_detal=Decimal("20000.00"),
                activo=1,
            )))
            db.commit()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.engine.dispose()

    @staticmethod
    def headers(role="ADMINISTRADOR"):
        token = create_access_token(1, role)
        return {"Authorization": f"Bearer {token}"}

    def test_protected_endpoint_requires_a_token_and_keeps_cors_headers(self):
        response = self.client.get(
            "/api/ventas",
            headers={"Origin": "http://localhost:5173"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Token requerido.")
        self.assertEqual(
            response.headers["access-control-allow-origin"],
            "http://localhost:5173",
        )

    def test_seller_cannot_access_dashboard_but_can_list_products(self):
        dashboard = self.client.get(
            "/api/dashboard/resumen",
            headers=self.headers("VENDEDOR"),
        )
        self.assertEqual(dashboard.status_code, 403)
        self.assertIn("permiso", dashboard.json()["detail"])

        products = self.client.get(
            "/api/comercial/productos",
            headers=self.headers("VENDEDOR"),
        )
        self.assertEqual(products.status_code, 200)
        self.assertEqual(len(products.json()), 1)
        self.assertEqual(
            products.json()[0]["sku_prenda"],
            "HTTP-TEST-001",
        )

    def test_seller_cannot_create_inventory_transfer(self):
        response = self.client.post(
            "/api/inventario/traslados",
            headers=self.headers("VENDEDOR"),
            json={},
        )

        self.assertEqual(response.status_code, 403)

    def test_pydantic_rejects_zero_quantity_before_service_execution(self):
        response = self.client.post(
            "/api/produccion/orden",
            headers=self.headers(),
            json={
                "id_area": 1,
                "sku_prenda": "HTTP-TEST-001",
                "cantidad_a_producir": 0,
                "fecha_entrega": "2026-10-28",
                "canal_destino": "DETAL",
            },
        )

        self.assertEqual(response.status_code, 422)
        errors = response.json()["detail"]
        self.assertTrue(any(
            error["loc"][-1] == "cantidad_a_producir"
            for error in errors
        ))

    def test_invalid_channel_is_rejected_with_validation_response(self):
        response = self.client.post(
            "/api/ventas",
            headers=self.headers(),
            json={
                "canal": "INVENTADO",
                "cliente": "Cliente",
                "detalles": [
                    {"sku_prenda": "HTTP-TEST-001", "cantidad": 1}
                ],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())

    def test_admin_can_set_material_minimum_and_read_low_stock_alerts(self):
        update = self.client.put(
            "/api/insumos/1/stock-minimo",
            headers=self.headers(),
            json={"stock_minimo": 3},
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.json()["stock_minimo"], 3)

        alerts = self.client.get(
            "/api/insumos/alertas-stock",
            headers=self.headers(),
        )
        self.assertEqual(alerts.status_code, 200)
        self.assertEqual(alerts.json()[0]["nombre_material"], "Tela HTTP")
        self.assertEqual(alerts.json()[0]["stock"], 2)

        dashboard = self.client.get(
            "/api/dashboard/resumen",
            headers=self.headers(),
        )
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.json()["insumos_bajo_minimo"], 1)
        self.assertEqual(
            dashboard.json()["alertas_insumos"][0]["nombre_material"],
            "Tela HTTP",
        )

    def test_worker_cannot_change_stock_minimum(self):
        response = self.client.put(
            "/api/insumos/1/stock-minimo",
            headers=self.headers("TRABAJADOR"),
            json={"stock_minimo": 3},
        )
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
