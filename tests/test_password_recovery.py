import os
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from werkzeug.security import check_password_hash, generate_password_hash

os.environ["SECRET_KEY"] = "unit-test-secret-key-at-least-32-bytes-long"

from backend.main import create_app
from backend.models.models import Usuario
from backend.security import create_access_token
from backend.services.auth_service import AuthService


class PasswordRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.client_context = TestClient(create_app(self.engine))
        self.client = self.client_context.__enter__()
        self.sent_codes = []
        self.sender_patch = patch.object(
            AuthService,
            "_send_recovery_email",
            side_effect=lambda address, code, name=None: self.sent_codes.append(
                (address, code)
            ),
        )
        self.sender_patch.start()

        with Session(self.engine) as db:
            db.add(
                Usuario(
                    id_usuario=10,
                    empleado="Usuario de prueba",
                    correo="usuario@yullita.com",
                    correo_recuperacion="usuario.real@example.com",
                    contrasenia=generate_password_hash("clave-anterior-segura"),
                    cedula_usuario="REC-10",
                    id_rol=2,
                    estado="ACTIVO",
                )
            )
            db.add(
                Usuario(
                    id_usuario=11,
                    empleado="Admin de prueba",
                    correo="admin@yullita.com",
                    correo_recuperacion=None,
                    contrasenia=generate_password_hash("clave-admin-segura"),
                    cedula_usuario="REC-11",
                    id_rol=1,
                    estado="ACTIVO",
                )
            )
            db.commit()

    def tearDown(self):
        self.sender_patch.stop()
        self.client_context.__exit__(None, None, None)
        self.engine.dispose()

    def request_code(self, destination="usuario.real@example.com"):
        return self.client.post(
            "/api/auth/forgot-password",
            json={
                "correo_acceso": "usuario@yullita.com",
                "correo_destino": destination,
            },
        )

    def reset_password(self, code, new_password="clave-nueva-segura-123"):
        return self.client.post(
            "/api/auth/reset-password",
            json={
                "correo_acceso": "usuario@yullita.com",
                "codigo": code,
                "nueva_contrasena": new_password,
            },
        )

    def test_code_is_sent_to_registered_email_and_resets_password_once(self):
        response = self.request_code()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.sent_codes[0][0], "usuario.real@example.com")
        code = self.sent_codes[0][1]
        self.assertRegex(code, r"^[0-9]{6}$")

        reset_response = self.reset_password(code)
        self.assertEqual(reset_response.status_code, 200)
        self.assertEqual(
            self.reset_password(code).status_code,
            400,
        )

        login = self.client.post(
            "/api/auth/login",
            json={
                "correo": "usuario@yullita.com",
                "contrasenia": "clave-nueva-segura-123",
            },
        )
        self.assertEqual(login.status_code, 200)

        with Session(self.engine) as db:
            user = db.query(Usuario).filter_by(id_usuario=10).one()
            self.assertTrue(
                check_password_hash(
                    user.contrasenia,
                    "clave-nueva-segura-123",
                )
            )
            self.assertIsNone(user.codigo_recuperacion_hash)

    def test_unknown_or_unregistered_email_does_not_send_code(self):
        response = self.request_code("attacker@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.sent_codes, [])

        response = self.client.post(
            "/api/auth/forgot-password",
            json={
                "correo_acceso": "missing@yullita.com",
                "correo_destino": "attacker@example.com",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.sent_codes, [])

    def test_expired_code_is_rejected_and_invalidated(self):
        self.request_code()
        with Session(self.engine) as db:
            user = db.query(Usuario).filter_by(id_usuario=10).one()
            user.codigo_recuperacion_expira = 1
            db.commit()

        response = self.reset_password(self.sent_codes[0][1])
        self.assertEqual(response.status_code, 400)
        with Session(self.engine) as db:
            user = db.query(Usuario).filter_by(id_usuario=10).one()
            self.assertIsNone(user.codigo_recuperacion_hash)

    def test_five_invalid_codes_invalidate_the_recovery_code(self):
        self.request_code()
        valid_code = self.sent_codes[0][1]
        wrong_code = "000000" if valid_code != "000000" else "000001"

        for _ in range(5):
            self.assertEqual(self.reset_password(wrong_code).status_code, 400)

        self.assertEqual(self.reset_password(valid_code).status_code, 400)

    def test_admin_can_configure_recovery_email_for_existing_accounts(self):
        token = create_access_token(11, "ADMINISTRADOR")
        response = self.client.put(
            "/api/auth/usuarios/10/correo-recuperacion",
            headers={"Authorization": f"Bearer {token}"},
            json={"correo_recuperacion": "nuevo.correo@example.com"},
        )
        self.assertEqual(response.status_code, 200)

        users = self.client.get(
            "/api/auth/usuarios",
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        updated_user = next(user for user in users if user["id_usuario"] == 10)
        self.assertEqual(
            updated_user["correo_recuperacion"],
            "nuevo.correo@example.com",
        )

    def test_recovery_email_is_multipart_with_personalized_responsive_html(self):
        message = AuthService._build_recovery_email(
            "usuario.real@example.com",
            "123456",
            "Ana & Luis",
        )

        self.assertEqual(message.get_content_type(), "multipart/alternative")
        plain_part, html_part = message.get_payload()
        plain_body = plain_part.get_payload(decode=True).decode("utf-8")
        html_body = html_part.get_payload(decode=True).decode("utf-8")

        self.assertEqual(plain_part.get_content_type(), "text/plain")
        self.assertIn("Tu código de verificación es: 123456", plain_body)
        self.assertEqual(html_part.get_content_type(), "text/html")
        self.assertIn("Hola, Ana &amp; Luis,", html_body)
        self.assertIn("letter-spacing:6px", html_body)
        self.assertIn("@media only screen and (max-width: 620px)", html_body)
        self.assertIn("vence en <strong", html_body)
        self.assertIn("Este es un correo automático", html_body)

    def test_incomplete_smtp_uses_console_fallback_only_in_development(self):
        self.sender_patch.stop()
        try:
            with patch.dict(
                os.environ,
                {
                    "APP_ENV": "development",
                    "SMTP_HOST": "smtp.gmail.com",
                    "SMTP_FROM_EMAIL": "",
                    "SMTP_USERNAME": "",
                    "SMTP_PASSWORD": "",
                },
                clear=True,
            ), patch("backend.services.auth_service.logger.warning") as warning:
                AuthService._send_recovery_email(
                    "user@example.test",
                    "123456",
                )
                warning.assert_called_once()

            with patch.dict(
                os.environ,
                {
                    "APP_ENV": "production",
                    "SMTP_HOST": "smtp.gmail.com",
                    "SMTP_FROM_EMAIL": "",
                    "SMTP_USERNAME": "",
                    "SMTP_PASSWORD": "",
                },
                clear=True,
            ):
                with self.assertRaises(HTTPException) as context:
                    AuthService._send_recovery_email(
                        "user@example.test",
                        "123456",
                    )
                self.assertEqual(context.exception.status_code, 503)
        finally:
            self.sender_patch.start()


if __name__ == "__main__":
    unittest.main()
