import asyncio
import os
import unittest

from fastapi import FastAPI, Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.middlewares.request_middleware import RequestMiddleware
from backend.models.models import Rol, Usuario
from backend.security import create_access_token

os.environ["SECRET_KEY"] = "unit-test-secret-key-at-least-32-bytes-long"


class RequestMiddlewareTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.application = FastAPI()
        self.application.state.session_factory = self.session_factory
        self.middleware = RequestMiddleware(self.application)
        with self.session_factory() as db:
            for role_id, role_name in (
                (1, "ADMINISTRADOR"),
                (2, "TRABAJADOR"),
                (3, "VENDEDOR"),
            ):
                db.add(Rol(id_rol=role_id, nombre_rol=role_name))
                db.add(
                    Usuario(
                        id_usuario=role_id,
                        empleado=role_name,
                        contrasenia="unused",
                        correo=f"{role_name.lower()}@example.test",
                        cedula_usuario=f"TEST-{role_id}",
                        id_rol=role_id,
                        estado="ACTIVO",
                    )
                )
            db.commit()

    def tearDown(self):
        self.engine.dispose()

    def response_status(self, path, method, role):
        user_id = {
            "ADMINISTRADOR": 1,
            "TRABAJADOR": 2,
            "VENDEDOR": 3,
        }[role]
        token = create_access_token(user_id, role)
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "root_path": "",
            "headers": [
                (b"host", b"localhost"),
                (b"authorization", f"Bearer {token}".encode()),
            ],
            "server": ("localhost", 80),
            "client": ("127.0.0.1", 12345),
            "app": self.application,
        }

        async def next_handler(_request):
            return Response(status_code=200)

        response = asyncio.run(
            self.middleware.dispatch(Request(scope), next_handler)
        )
        return response.status_code

    def test_dashboard_is_admin_only(self):
        self.assertEqual(
            self.response_status(
                "/api/dashboard/resumen",
                "GET",
                "VENDEDOR",
            ),
            403,
        )
        self.assertEqual(
            self.response_status(
                "/api/dashboard/resumen",
                "GET",
                "ADMINISTRADOR",
            ),
            200,
        )

    def test_sales_and_inventory_writes_follow_role_permissions(self):
        self.assertEqual(
            self.response_status("/api/ventas", "GET", "TRABAJADOR"),
            403,
        )
        self.assertEqual(
            self.response_status("/api/ventas", "GET", "VENDEDOR"),
            200,
        )
        self.assertEqual(
            self.response_status(
                "/api/inventario/traslados",
                "POST",
                "VENDEDOR",
            ),
            403,
        )
        self.assertEqual(
            self.response_status("/api/insumos/catalogo", "GET", "VENDEDOR"),
            403,
        )
        self.assertEqual(
            self.response_status("/api/produccion/areas", "GET", "VENDEDOR"),
            403,
        )
        self.assertEqual(
            self.response_status("/api/pedidos", "POST", "VENDEDOR"),
            200,
        )

    def test_existing_token_uses_current_database_role(self):
        with self.session_factory() as db:
            user = db.query(Usuario).filter_by(id_usuario=3).one()
            token = create_access_token(user.id_usuario, "VENDEDOR")
            user.id_rol = 2
            db.commit()

        self.assertEqual(
            self.response_status_with_token(
                "/api/ventas",
                "GET",
                token,
            ),
            403,
        )

    def response_status_with_token(self, path, method, token):
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "root_path": "",
            "headers": [
                (b"host", b"localhost"),
                (b"authorization", f"Bearer {token}".encode()),
            ],
            "server": ("localhost", 80),
            "client": ("127.0.0.1", 12345),
            "app": self.application,
        }

        async def next_handler(_request):
            return Response(status_code=200)

        response = asyncio.run(
            self.middleware.dispatch(Request(scope), next_handler)
        )
        return response.status_code


if __name__ == "__main__":
    unittest.main()
