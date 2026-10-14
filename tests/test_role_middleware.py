import asyncio
import unittest

from fastapi import Request, Response

from backend.middlewares.request_middleware import RequestMiddleware
from backend.security import create_access_token


class RequestMiddlewareTests(unittest.TestCase):
    def setUp(self):
        self.middleware = RequestMiddleware(None)

    def response_status(self, path, method, role):
        token = create_access_token(1, role)
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


if __name__ == "__main__":
    unittest.main()
