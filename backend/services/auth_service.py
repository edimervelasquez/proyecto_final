import hashlib
import html
import hmac
import logging
import os
import secrets
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from backend.repositories.auth_repository import AuthRepository
from backend.models.models import Rol, Usuario
from backend.schemas.auth_schema import (
    CorreoRecuperacionUpdate,
    RestablecerContrasena,
    SolicitudRecuperacionContrasena,
    UsuarioAdminBootstrap,
    UsuarioLogin,
    UsuarioRegistro,
)
from backend.security import create_access_token, get_secret_key

logger = logging.getLogger("backend.auth")
RECOVERY_CODE_TTL_SECONDS = 10 * 60
RECOVERY_CODE_MAX_ATTEMPTS = 5


class AuthService:

    @staticmethod
    def _commit(db: Session):
        try:
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="No se pudieron guardar los cambios de usuario.",
            ) from exc

    @staticmethod
    def login_service(data: UsuarioLogin, db: Session):
        usuario = AuthRepository.obtener_por_correo(db, data.correo)
        if not usuario or not AuthService._verify_password(
            usuario.contrasenia, data.contrasenia
        ):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

        if not AuthService._is_password_hash(usuario.contrasenia):
            usuario.contrasenia = generate_password_hash(data.contrasenia)
            AuthService._commit(db)

        if not usuario.estado or usuario.estado.upper() not in ("ACTIVO", "APROBADO"):
            raise HTTPException(status_code=403, detail="Tu cuenta está pendiente de aprobación.")

        rol_obj = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
        nombre_rol = rol_obj.nombre_rol if rol_obj else "TRABAJADOR"

        return {
            "mensaje": "Inicio de sesión exitoso.",
            "access_token": create_access_token(usuario.id_usuario, nombre_rol),
            "token_type": "bearer",
            "usuario": {
                "id_usuario": usuario.id_usuario,
                "empleado": usuario.empleado,
                "correo": usuario.correo,
                "id_rol": usuario.id_rol,
                "rol": nombre_rol,
                "estado": usuario.estado
            }
        }

    @staticmethod
    def registrar_service(data: UsuarioRegistro, db: Session):
        existe = AuthRepository.obtener_por_correo(db, data.correo)
        if existe:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

        usuario_dict = {
            "empleado": data.empleado,
            "correo": data.correo,
            "correo_recuperacion": data.correo_recuperacion,
            "contrasenia": generate_password_hash(data.contrasenia),
            "cedula_usuario": data.cedula,
            "id_rol": data.id_rol,
            "estado": "PENDIENTE",
        }

        AuthRepository.crear_usuario(db, usuario_dict)
        AuthService._commit(db)
        return {
            "mensaje": (
                "¡Usuario creado con éxito! Tu cuenta está pendiente de aprobación."
            )
        }

    @staticmethod
    def bootstrap_admin_service(
        data: UsuarioAdminBootstrap,
        provided_token: str | None,
        db: Session,
    ):
        configured_token = os.environ.get("INITIAL_ADMIN_TOKEN", "")
        if len(configured_token.encode("utf-8")) < 32:
            raise HTTPException(
                status_code=503,
                detail="La creación inicial de administrador no está configurada.",
            )
        if not provided_token or not hmac.compare_digest(
            provided_token, configured_token
        ):
            raise HTTPException(
                status_code=403,
                detail="Token de inicialización inválido.",
            )

        admin_role = (
            db.query(Rol)
            .filter(Rol.id_rol == 1)
            .with_for_update()
            .first()
        )
        if admin_role is None:
            raise HTTPException(
                status_code=503,
                detail="El rol administrador no está inicializado.",
            )
        if db.query(Usuario).filter(Usuario.id_rol == 1).first():
            raise HTTPException(
                status_code=409,
                detail="Ya existe una cuenta administradora; no se permite reiniciar.",
            )

        if AuthRepository.obtener_por_correo(db, data.correo):
            raise HTTPException(
                status_code=400,
                detail="El correo electrónico ya está registrado.",
            )

        AuthRepository.crear_usuario(
            db,
            {
                "empleado": data.empleado,
                "correo": data.correo,
                "correo_recuperacion": data.correo_recuperacion,
                "contrasenia": generate_password_hash(data.contrasenia),
                "cedula_usuario": data.cedula,
                "id_rol": 1,
                "estado": "ACTIVO",
            },
        )
        AuthService._commit(db)
        return {
            "mensaje": "Cuenta de administrador creada. Ya puedes iniciar sesión."
        }

    @staticmethod
    def solicitar_recuperacion_service(
        data: SolicitudRecuperacionContrasena,
        db: Session,
    ):
        usuario = AuthRepository.obtener_por_correo_para_actualizacion(
            db,
            data.correo_acceso,
        )
        if (
            usuario is None
            or not usuario.correo_recuperacion
            or not hmac.compare_digest(
                usuario.correo_recuperacion.casefold(),
                data.correo_destino.casefold(),
            )
        ):
            return {
                "mensaje": (
                    "Si los datos corresponden a una cuenta, enviaremos un "
                    "código al correo de recuperación registrado."
                )
            }

        codigo = f"{secrets.randbelow(1_000_000):06d}"
        usuario.codigo_recuperacion_hash = AuthService._hash_recovery_code(codigo)
        usuario.codigo_recuperacion_expira = (
            int(time.time()) + RECOVERY_CODE_TTL_SECONDS
        )
        usuario.intentos_codigo_recuperacion = 0
        AuthService._commit(db)

        try:
            AuthService._send_recovery_email(
                usuario.correo_recuperacion,
                codigo,
                usuario.empleado,
            )
        except HTTPException:
            usuario.codigo_recuperacion_hash = None
            usuario.codigo_recuperacion_expira = None
            usuario.intentos_codigo_recuperacion = 0
            AuthService._commit(db)
            raise

        return {
            "mensaje": (
                "Si los datos corresponden a una cuenta, enviaremos un "
                "código al correo de recuperación registrado."
            )
        }

    @staticmethod
    def _send_recovery_email(
        correo_destino: str,
        codigo: str,
        nombre_usuario: str | None = None,
    ):
        host = os.environ.get("SMTP_HOST", "").strip()
        if not host:
            if AuthService._log_recovery_code_in_development(
                correo_destino,
                codigo,
            ):
                return
            raise HTTPException(
                status_code=503,
                detail="El servicio de correo no está configurado.",
            )

        remitente = os.environ.get(
            "SMTP_FROM_EMAIL",
            os.environ.get("SMTP_USERNAME", ""),
        ).strip()
        usuario_smtp = os.environ.get("SMTP_USERNAME", "").strip()
        clave_smtp = os.environ.get("SMTP_PASSWORD", "")
        if not remitente or (usuario_smtp and not clave_smtp):
            if AuthService._log_recovery_code_in_development(
                correo_destino,
                codigo,
            ):
                return
            raise HTTPException(
                status_code=503,
                detail="La configuración del servicio de correo está incompleta.",
            )
        try:
            puerto = int(os.environ.get("SMTP_PORT", "587"))
        except ValueError as exc:
            raise HTTPException(
                status_code=503,
                detail="La configuración del servicio de correo no es válida.",
            ) from exc
        mensaje = AuthService._build_recovery_email(
            correo_destino,
            codigo,
            nombre_usuario,
        )

        use_ssl = os.environ.get("SMTP_USE_SSL", "false").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        use_tls = os.environ.get("SMTP_USE_TLS", "true").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        try:
            if use_ssl:
                with smtplib.SMTP_SSL(host, puerto, timeout=10) as smtp:
                    if usuario_smtp:
                        smtp.login(usuario_smtp, clave_smtp)
                    smtp.send_message(mensaje)
            else:
                with smtplib.SMTP(host, puerto, timeout=10) as smtp:
                    if use_tls:
                        smtp.starttls()
                    if usuario_smtp:
                        smtp.login(usuario_smtp, clave_smtp)
                    smtp.send_message(mensaje)
        except (OSError, smtplib.SMTPException) as exc:
            logger.exception("No se pudo enviar el correo de recuperación.")
            raise HTTPException(
                status_code=503,
                detail="No se pudo enviar el correo de recuperación.",
            ) from exc

    @staticmethod
    def _log_recovery_code_in_development(
        correo_destino: str,
        codigo: str,
    ) -> bool:
        if os.environ.get("APP_ENV", "").strip().lower() != "development":
            return False
        logger.warning(
            "Codigo de recuperacion de contrasena para %s: %s",
            correo_destino,
            codigo,
        )
        return True

    @staticmethod
    def _build_recovery_email(
        correo_destino: str,
        codigo: str,
        nombre_usuario: str | None = None,
    ) -> MIMEMultipart:
        remitente = os.environ.get(
            "SMTP_FROM_EMAIL",
            os.environ.get("SMTP_USERNAME", ""),
        ).strip()
        saludo = f"Hola, {nombre_usuario.strip()}," if nombre_usuario else "Hola,"
        saludo_html = html.escape(saludo)

        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = "Código para recuperar tu contraseña - SIES Yullita"
        mensaje["From"] = remitente
        mensaje["To"] = correo_destino
        texto_plano = (
            f"{saludo}\n\n"
            "Recibimos una solicitud para restablecer la contraseña de tu "
            "cuenta de SIES Yullita.\n\n"
            f"Tu código de verificación es: {codigo}\n"
            "El código vence en 10 minutos y solo puede utilizarse una vez.\n"
            "Si no solicitaste este cambio, puedes ignorar este mensaje."
        )
        codigo_html = html.escape(codigo)
        html_body = f"""\
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="dark">
    <meta name="supported-color-schemes" content="dark">
    <title>Recuperación de contraseña | SIES Yullita</title>
    <style>
      @media only screen and (max-width: 620px) {{
        .email-shell {{ padding: 18px 10px !important; }}
        .email-card {{ padding: 28px 20px !important; }}
        .otp-code {{ font-size: 30px !important; letter-spacing: 5px !important; }}
      }}
    </style>
  </head>
  <body style="margin:0; padding:0; background-color:#0b0f19; color:#e5e7eb; font-family:Arial, Helvetica, sans-serif;">
    <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%; background-color:#0b0f19; border-collapse:collapse;">
      <tr>
        <td align="center" class="email-shell" style="padding:40px 16px;">
          <table role="presentation" width="600" border="0" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; border:1px solid #1f2937; border-radius:16px; background-color:#111827; border-collapse:separate;">
            <tr>
              <td class="email-card" style="padding:40px;">
                <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="width:100%; border-collapse:collapse;">
                  <tr>
                    <td style="padding-bottom:8px; color:#f59e0b; font-size:13px; font-weight:bold; letter-spacing:2px; text-transform:uppercase;">
                      SIES Yullita
                    </td>
                  </tr>
                  <tr>
                    <td style="padding-bottom:30px; border-bottom:1px solid #1f2937; color:#9ca3af; font-size:13px; line-height:20px;">
                      Sistema Integral de Gestión Textil y Comercial
                    </td>
                  </tr>
                  <tr>
                    <td style="padding-top:30px; color:#f9fafb; font-size:24px; font-weight:bold; line-height:32px;">
                      {saludo_html}
                    </td>
                  </tr>
                  <tr>
                    <td style="padding-top:14px; color:#d1d5db; font-size:16px; line-height:25px;">
                      Recibimos una solicitud para restablecer la contraseña de tu cuenta.
                      Usa el siguiente código para continuar:
                    </td>
                  </tr>
                  <tr>
                    <td align="center" style="padding:28px 0;">
                      <table role="presentation" border="0" cellspacing="0" cellpadding="0" style="border-collapse:separate;">
                        <tr>
                          <td class="otp-code" align="center" style="padding:20px 28px; border:1px solid #f59e0b; border-radius:12px; background-color:#0b0f19; color:#fbbf24; font-family:'Courier New', Courier, monospace; font-size:36px; font-weight:bold; letter-spacing:6px; line-height:44px;">
                            {codigo_html}
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:16px 18px; border:1px solid #374151; border-radius:10px; background-color:#0b0f19; color:#cbd5e1; font-size:14px; line-height:22px;">
                      <strong style="color:#f59e0b;">Aviso de seguridad:</strong>
                      este código vence en <strong style="color:#f9fafb;">10 minutos</strong>
                      y solo puede utilizarse una vez. Si no solicitaste este cambio,
                      puedes ignorar este correo con tranquilidad.
                    </td>
                  </tr>
                  <tr>
                    <td style="padding-top:28px; color:#9ca3af; font-size:13px; line-height:20px;">
                      Por seguridad, nunca compartas este código con otras personas.
                    </td>
                  </tr>
                  <tr>
                    <td style="padding-top:28px; border-top:1px solid #1f2937; color:#9ca3af; font-size:12px; line-height:19px;">
                      © SIES Yullita — Seguridad y Gestión Empresarial<br>
                      Este es un correo automático; por favor, no respondas a este mensaje.
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""
        mensaje.attach(MIMEText(texto_plano, "plain", "utf-8"))
        mensaje.attach(MIMEText(html_body, "html", "utf-8"))
        return mensaje

    @staticmethod
    def restablecer_contrasena_service(
        data: RestablecerContrasena,
        db: Session,
    ):
        usuario = AuthRepository.obtener_por_correo_para_actualizacion(
            db,
            data.correo_acceso,
        )
        codigo_hash = AuthService._hash_recovery_code(data.codigo)
        if (
            usuario is None
            or not usuario.codigo_recuperacion_hash
            or usuario.codigo_recuperacion_expira is None
        ):
            raise HTTPException(
                status_code=400,
                detail="El código es inválido o ha expirado.",
            )

        if (
            usuario.codigo_recuperacion_expira <= int(time.time())
            or usuario.intentos_codigo_recuperacion >= RECOVERY_CODE_MAX_ATTEMPTS
        ):
            AuthService._clear_recovery_code(usuario)
            AuthService._commit(db)
            raise HTTPException(
                status_code=400,
                detail="El código es inválido o ha expirado.",
            )

        if not hmac.compare_digest(usuario.codigo_recuperacion_hash, codigo_hash):
            usuario.intentos_codigo_recuperacion += 1
            if usuario.intentos_codigo_recuperacion >= RECOVERY_CODE_MAX_ATTEMPTS:
                AuthService._clear_recovery_code(usuario)
            AuthService._commit(db)
            raise HTTPException(
                status_code=400,
                detail="El código es inválido o ha expirado.",
            )

        usuario.contrasenia = generate_password_hash(data.nueva_contrasena)
        AuthService._clear_recovery_code(usuario)
        AuthService._commit(db)
        return {"mensaje": "La contraseña se actualizó correctamente."}

    @staticmethod
    def _clear_recovery_code(usuario: Usuario):
        usuario.codigo_recuperacion_hash = None
        usuario.codigo_recuperacion_expira = None
        usuario.intentos_codigo_recuperacion = 0

    @staticmethod
    def _hash_recovery_code(codigo: str) -> str:
        return hmac.new(
            get_secret_key(),
            codigo.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def _is_password_hash(password: str) -> bool:
        return password.startswith(("scrypt:", "pbkdf2:"))

    @staticmethod
    def _verify_password(stored_password: str, provided_password: str) -> bool:
        if AuthService._is_password_hash(stored_password):
            return check_password_hash(stored_password, provided_password)
        return hmac.compare_digest(stored_password, provided_password)

    @staticmethod
    def listar_usuarios_service(db: Session):
        return [
            {
                "id_usuario": usuario.id_usuario,
                "empleado": usuario.empleado,
                "correo": usuario.correo,
                "correo_recuperacion": usuario.correo_recuperacion,
                "cedula": usuario.cedula_usuario,
                "id_rol": usuario.id_rol,
                "rol": nombre_rol or "TRABAJADOR",
                "estado": usuario.estado,
            }
            for usuario, nombre_rol in AuthRepository.obtener_usuarios_con_rol(db)
        ]

    @staticmethod
    def actualizar_correo_recuperacion_service(
        user_id: int,
        data: CorreoRecuperacionUpdate,
        db: Session,
    ):
        usuario = AuthRepository.obtener_por_id(db, user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        if usuario.correo_recuperacion != data.correo_recuperacion:
            usuario.correo_recuperacion = data.correo_recuperacion
            AuthService._clear_recovery_code(usuario)
            AuthService._commit(db)
        return {"mensaje": "Correo de recuperación actualizado correctamente."}

    @staticmethod
    def cambiar_estado_usuario_service(user_id: int, estado: str, db: Session):
        estado_limpio = estado.strip('"').strip("'").upper()
        usuario = AuthRepository.actualizar_estado_usuario(db, user_id, estado_limpio)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        AuthService._commit(db)
        return {"mensaje": f"El estado del usuario fue actualizado a {estado_limpio} correctamente."}

    @staticmethod
    def cambiar_rol_usuario_service(user_id: int, id_rol: int, db: Session):
        if id_rol not in (1, 2, 3):
            raise HTTPException(status_code=400, detail="Rol no válido.")
        usuario = AuthRepository.obtener_por_id(db, user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        if usuario.id_rol == 1 and id_rol != 1:
            administradores_activos = db.query(Usuario).filter(
                Usuario.id_rol == 1,
                Usuario.estado.in_(["ACTIVO", "APROBADO"]),
            ).count()
            if administradores_activos <= 1:
                raise HTTPException(
                    status_code=409,
                    detail="No se puede cambiar el rol del último administrador activo.",
                )
        actualizado = AuthRepository.actualizar_rol_usuario(db, user_id, id_rol)
        AuthService._commit(db)
        roles = {1: "ADMINISTRADOR", 2: "TRABAJADOR", 3: "VENDEDOR"}
        return {
            "mensaje": f"Rol actualizado a {roles[id_rol]}.",
            "id_usuario": actualizado.id_usuario,
            "id_rol": actualizado.id_rol,
        }

    @staticmethod
    def eliminar_usuario_service(user_id: int, db: Session):
        usuario = AuthRepository.eliminar_usuario(db, user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        AuthService._commit(db)
        return {"mensaje": "Usuario eliminado correctamente."}