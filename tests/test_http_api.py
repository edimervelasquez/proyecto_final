import os
import unittest
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.main import create_app
from backend.models.models import MateriaPrima, ProductoComercial, Usuario
from backend.models.models import (
    Area,
    DetalleVenta,
    IngresoInsumos,
    FichaTecnicaInsumo,
    InventarioPrenda,
    MateriaPrima,
    Modelo,
    MovimientoPrenda,
    OrdenComercial,
    Produccion,
    TrazoProduccion,
)
from backend.security import create_access_token, get_secret_key

os.environ["SECRET_KEY"] = "unit-test-secret-key-at-least-32-bytes-long"
os.environ["INITIAL_ADMIN_TOKEN"] = (
    "unit-test-initial-admin-token-at-least-32-bytes-long"
)


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
            user = Usuario(
                id_usuario=1,
                empleado="Admin HTTP",
                contrasenia="hash",
                correo="admin-http@example.test",
                cedula_usuario="HTTP-ADMIN",
                id_rol=1,
                estado="ACTIVO",
            )
            worker = Usuario(
                id_usuario=2,
                empleado="Worker HTTP",
                contrasenia="hash",
                correo="worker-http@example.test",
                cedula_usuario="HTTP-WORKER",
                id_rol=2,
                estado="ACTIVO",
            )
            seller = Usuario(
                id_usuario=3,
                empleado="Seller HTTP",
                contrasenia="hash",
                correo="seller-http@example.test",
                cedula_usuario="HTTP-SELLER",
                id_rol=3,
                estado="ACTIVO",
            )
            material = MateriaPrima(
                id_materiaPrima=1,
                nombre_material="Tela HTTP",
                Cantidad_materiaPrima=2,
                stock_minimo=0,
            )
            db.add_all(
                (
                    user,
                    worker,
                    seller,
                    material,
                    ProductoComercial(
                        sku_prenda="HTTP-TEST-001",
                        nombre_producto="Producto para prueba HTTP",
                        descripcion="Registro exclusivo de pruebas",
                        costo_mano_obra=Decimal("2000.00"),
                        precio_mayorista=Decimal("12000.00"),
                        precio_detal=Decimal("20000.00"),
                        activo=1,
                    ),
                )
            )
            db.commit()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.engine.dispose()

    @staticmethod
    def headers(role="ADMINISTRADOR"):
        user_id = {"ADMINISTRADOR": 1, "TRABAJADOR": 2, "VENDEDOR": 3}[role]
        token = create_access_token(user_id, role)
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

    def test_admin_can_create_new_material_by_setting_existing_id_to_null(self):
        openapi = self.client.get("/openapi.json").json()
        ingreso_schema = openapi["components"]["schemas"]["IngresoInsumoCreate"]
        self.assertEqual(len(ingreso_schema["examples"]), 2)

        response = self.client.post(
            "/api/insumos/ingreso",
            headers=self.headers("ADMINISTRADOR"),
            json={
                "id_materiaPrima": None,
                "nombre_material": "Tela creada desde Swagger",
                "cantidad": 5,
                "proveedor": "Proveedor de prueba",
                "costo_unitario": 1200,
                "stock_minimo": 1,
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["nombre_material"], "Tela creada desde Swagger")
        self.assertEqual(response.json()["nuevo_stock"], 5)

        with Session(self.engine) as db:
            material = db.query(MateriaPrima).filter_by(
                nombre_material="Tela creada desde Swagger"
            ).one()
            ingreso = db.query(IngresoInsumos).filter_by(
                id_entrante=response.json()["id_ingreso"]
            ).one()
            self.assertEqual(material.Cantidad_materiaPrima, 5)
            self.assertEqual(ingreso.id_materiaPrima, material.id_materiaPrima)

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

    def test_pedido_requires_auth_and_a_production_lot(self):
        openapi = self.client.get("/openapi.json").json()
        operation = openapi["paths"]["/api/pedidos"]["post"]
        self.assertIn("Pedidos", operation["tags"])
        self.assertTrue(operation["security"])
        self.assertTrue(
            openapi["paths"]["/api/insumos/catalogo"]["get"]["security"]
        )
        self.assertTrue(
            openapi["paths"]["/api/produccion/areas"]["get"]["security"]
        )
        self.assertIn("/api/produccion/trazos", openapi["paths"])
        self.assertTrue(
            openapi["paths"]["/api/produccion/trazos"]["post"]["security"]
        )
        order_schema = openapi["components"]["schemas"]["OrdenProduccionCreate"]
        self.assertIn("id_trazos", order_schema["properties"])

        unauthorized = self.client.post("/api/pedidos", json={})
        self.assertEqual(unauthorized.status_code, 401)

        missing_lot = self.client.post(
            "/api/pedidos",
            headers=self.headers("VENDEDOR"),
            json={
                "canal": "DETAL",
                "cliente": "Cliente",
                "detalles": [
                    {"sku_prenda": "HTTP-TEST-001", "cantidad": 1}
                ],
            },
        )
        self.assertEqual(missing_lot.status_code, 422)
        self.assertIn("id_produccion", str(missing_lot.json()["detail"]))

        authorized_seller = self.client.post(
            "/api/pedidos",
            headers=self.headers("VENDEDOR"),
            json={
                "canal": "DETAL",
                "cliente": "Cliente",
                "detalles": [
                    {
                        "sku_prenda": "HTTP-TEST-001",
                        "cantidad": 1,
                        "id_produccion": 99999,
                    }
                ],
            },
        )
        self.assertEqual(authorized_seller.status_code, 404)
        self.assertIn("producción", authorized_seller.json()["detail"])

        with Session(self.engine) as db:
            area = db.query(Area).filter_by(
                nombre_area="Calidad y Empaque"
            ).one()
            ingreso = IngresoInsumos(
                id_materiaPrima=1,
                cantidad_materia_prima=1,
                proveedor="Prueba de pedido",
                costo_unitario=Decimal("2.00"),
                fecha_ingreso=date.today(),
            )
            db.add(ingreso)
            db.flush()
            modelo = Modelo(nombre_modelo="Modelo de pedido")
            db.add(modelo)
            db.flush()
            order = Produccion(
                id_modelo=modelo.id_modelo,
                id_area=area.id_area,
                id_ingreso_insumos=ingreso.id_entrante,
                fecha_recibido=date.today(),
                fecha_entrega=date.today(),
                cantidad_recibida=2,
                cantidad_entregada=2,
            )
            db.add(order)
            db.flush()
            db.add_all((
                OrdenComercial(
                    id_produccion=order.id_produccion,
                    sku_prenda="HTTP-TEST-001",
                    canal_destino="DETAL",
                    costo_unitario_estimado=Decimal("2000.00"),
                ),
                InventarioPrenda(
                    sku_prenda="HTTP-TEST-001",
                    ubicacion="LOCAL",
                    cantidad=2,
                    costo_promedio=Decimal("2000.00"),
                ),
                MovimientoPrenda(
                    sku_prenda="HTTP-TEST-001",
                    ubicacion="LOCAL",
                    tipo_movimiento="PRODUCCION_APROBADA",
                    cantidad=2,
                    costo_unitario=Decimal("2000.00"),
                    referencia=f"OP-{order.id_produccion}",
                    id_produccion=order.id_produccion,
                    id_usuario=1,
                ),
            ))
            db.commit()
            production_id = order.id_produccion

        created = self.client.post(
            "/api/pedidos",
            headers=self.headers("VENDEDOR"),
            json={
                "canal": "DETAL",
                "cliente": "Pedido trazable",
                "detalles": [
                    {
                        "sku_prenda": "HTTP-TEST-001",
                        "cantidad": 1,
                        "id_produccion": production_id,
                    }
                ],
            },
        )
        self.assertEqual(created.status_code, 201, created.text)
        self.assertEqual(created.json()["cliente"], "Pedido trazable")
        with Session(self.engine) as db:
            detail = db.query(DetalleVenta).filter_by(
                id_venta=created.json()["id_venta"]
            ).one()
            self.assertEqual(detail.id_produccion, production_id)
            movement = db.query(MovimientoPrenda).filter_by(
                referencia=f"VENTA-{created.json()['id_venta']}"
            ).one()
            self.assertEqual(movement.id_produccion, production_id)
            stock = db.query(InventarioPrenda).filter_by(
                sku_prenda="HTTP-TEST-001",
                ubicacion="LOCAL",
            ).one()
            self.assertEqual(stock.cantidad, 1)

    def test_swagger_trace_endpoint_persists_material_receipt_and_product_link(self):
        with Session(self.engine) as db:
            ingreso = IngresoInsumos(
                id_materiaPrima=1,
                cantidad_materia_prima=10,
                proveedor="Ingreso trazable",
                costo_unitario=Decimal("5.00"),
                fecha_ingreso=date.today(),
            )
            db.add(ingreso)
            db.flush()
            db.add(FichaTecnicaInsumo(
                sku_prenda="HTTP-TEST-001",
                id_materiaPrima=1,
                cantidad_estimada=Decimal("0.50"),
            ))
            db.commit()
            ingreso_id = ingreso.id_entrante

        created = self.client.post(
            "/api/produccion/trazos",
            headers=self.headers("TRABAJADOR"),
            json={
                "id_ingreso": ingreso_id,
                "sku_prenda": "HTTP-TEST-001",
                "cantidad_materia_prima": "1.00",
                "cantidad_prendas": 2,
                "observaciones": "Trazado de prueba",
            },
        )
        self.assertEqual(created.status_code, 201, created.text)
        self.assertEqual(created.json()["id_ingreso"], ingreso_id)
        self.assertEqual(created.json()["id_materiaPrima"], 1)
        self.assertEqual(created.json()["sku_prenda"], "HTTP-TEST-001")
        self.assertIsNone(created.json()["id_produccion"])

        listed = self.client.get(
            "/api/produccion/trazos",
            headers=self.headers("TRABAJADOR"),
        )
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()[0]["id_trazo"], created.json()["id_trazo"])

        with Session(self.engine) as db:
            stored = db.query(TrazoProduccion).filter_by(
                id_trazo=created.json()["id_trazo"]
            ).one()
            self.assertEqual(stored.id_ingreso, ingreso_id)
            self.assertEqual(stored.cantidad_prendas, 2)

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

    def test_registration_requires_strong_password_and_never_grants_admin(self):
        response = self.client.post(
            "/api/auth/registrar",
            json={
                "empleado": "Nuevo Usuario",
                "correo": "new-user@example.com",
                "contrasenia": "corta",
                "cedula": "NEW-USER",
                "id_rol": 2,
            },
        )
        self.assertEqual(response.status_code, 422)

        response = self.client.post(
            "/api/auth/registrar",
            json={
                "empleado": "Nuevo Usuario",
                "correo": "new-user@example.com",
                "contrasenia": "una-clave-segura-123",
                "cedula": "NEW-USER",
                "id_rol": 2,
            },
        )
        self.assertEqual(response.status_code, 201)
        with Session(self.engine) as db:
            registered = db.query(Usuario).filter_by(
                correo="new-user@example.com"
            ).one()
            self.assertEqual(registered.id_rol, 2)
            self.assertEqual(registered.estado, "PENDIENTE")

    def test_bootstrap_admin_is_secret_protected_and_one_time(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        payload = {
            "empleado": "Admin Bootstrap",
            "correo": "bootstrap-admin@example.com",
            "contrasenia": "una-clave-segura-123",
            "cedula": "BOOTSTRAP-ADMIN",
        }
        try:
            with TestClient(create_app(engine)) as client:
                response = client.post(
                    "/api/auth/bootstrap-admin",
                    headers={"X-Initial-Admin-Token": "token-incorrecto"},
                    json=payload,
                )
                self.assertEqual(response.status_code, 403)

                response = client.post(
                    "/api/auth/registrar",
                    json={
                        "empleado": "Primer Usuario",
                        "correo": "first-user@example.com",
                        "contrasenia": "una-clave-segura-123",
                        "cedula": "FIRST-USER",
                        "id_rol": 3,
                    },
                )
                self.assertEqual(response.status_code, 201)

                response = client.post(
                    "/api/auth/bootstrap-admin",
                    headers={
                        "X-Initial-Admin-Token": os.environ["INITIAL_ADMIN_TOKEN"]
                    },
                    json=payload,
                )
                self.assertEqual(response.status_code, 201)

                response = client.post(
                    "/api/auth/bootstrap-admin",
                    headers={
                        "X-Initial-Admin-Token": os.environ["INITIAL_ADMIN_TOKEN"]
                    },
                    json=payload,
                )
                self.assertEqual(response.status_code, 409)
        finally:
            engine.dispose()

    def test_secret_key_must_be_configured_and_cors_must_be_explicit(self):
        with patch.dict(os.environ, {"SECRET_KEY": "short"}):
            with self.assertRaises(RuntimeError):
                get_secret_key()

        with patch.dict(os.environ, {"SECRET_KEY": "x" * 32}):
            self.assertEqual(len(get_secret_key()), 32)

        with patch.dict(os.environ, {"CORS_ALLOWED_ORIGINS": "*"}):
            with self.assertRaises(ValueError):
                create_app(self.engine)

    def test_existing_token_loses_access_after_account_is_deactivated(self):
        token = create_access_token(3, "VENDEDOR")
        with Session(self.engine) as db:
            db.query(Usuario).filter_by(id_usuario=3).update(
                {"estado": "INACTIVO"}
            )
            db.commit()

        response = self.client.get(
            "/api/ventas",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["detail"],
            "La cuenta no existe o está inactiva.",
        )


if __name__ == "__main__":
    unittest.main()
