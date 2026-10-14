from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from backend.models.models import Trazabilidad, Usuario


class TrazabilidadRepository:

    @staticmethod
    def registrar(
        db: Session,
        tipo_registro: str,
        referencia: str,
        nombre_registro: str,
        id_usuario: int,
        proceso: str,
        estado: str,
        descripcion: Optional[str] = None,
    ):
        registro = Trazabilidad(
            tipo_registro=tipo_registro,
            referencia=str(referencia),
            nombre_registro=nombre_registro,
            id_usuario=id_usuario,
            proceso=proceso,
            estado=estado,
            descripcion=descripcion,
        )
        db.add(registro)
        return registro

    @staticmethod
    def obtener_por_tipo(db: Session, tipo_registro: str):
        filas = (
            db.query(Trazabilidad, Usuario.empleado)
            .join(Usuario, Usuario.id_usuario == Trazabilidad.id_usuario)
            .filter(Trazabilidad.tipo_registro == tipo_registro)
            .all()
        )
        return {
            registro.referencia: {
                "nombre_registro": registro.nombre_registro,
                "registrado_por": empleado,
                "fecha_registro": registro.fecha_registro.isoformat()
                if registro.fecha_registro
                else None,
                "proceso": registro.proceso,
                "estado": registro.estado,
                "descripcion": registro.descripcion,
            }
            for registro, empleado in filas
        }

    @staticmethod
    def obtener_recientes(db: Session, limite: int = 10):
        filas = (
            db.query(Trazabilidad, Usuario.empleado)
            .join(Usuario, Usuario.id_usuario == Trazabilidad.id_usuario)
            .order_by(Trazabilidad.fecha_registro.desc(), Trazabilidad.id_trazabilidad.desc())
            .limit(limite)
            .all()
        )
        return [
            {
                "tipo_registro": registro.tipo_registro,
                "referencia": registro.referencia,
                "nombre_registro": registro.nombre_registro,
                "registrado_por": empleado,
                "fecha_registro": registro.fecha_registro.isoformat()
                if registro.fecha_registro
                else None,
                "proceso": registro.proceso,
                "estado": registro.estado,
            }
            for registro, empleado in filas
        ]

    @staticmethod
    def actualizar_estado(
        db: Session,
        tipo_registro: str,
        referencia: str,
        estado: str,
        proceso: str,
        actualizado_por: int,
        crear_si_no_existe: bool = False,
    ):
        registro = (
            db.query(Trazabilidad)
            .filter(
                Trazabilidad.tipo_registro == tipo_registro,
                Trazabilidad.referencia == str(referencia),
            )
            .first()
        )
        if registro:
            registro.estado = estado
            registro.proceso = proceso
            registro.actualizado_por = actualizado_por
            registro.fecha_actualizacion = func.now()
        elif crear_si_no_existe:
            registro = Trazabilidad(
                tipo_registro=tipo_registro,
                referencia=str(referencia),
                nombre_registro=f"OP-{referencia}",
                id_usuario=actualizado_por,
                proceso=proceso,
                estado=estado,
                actualizado_por=actualizado_por,
                fecha_actualizacion=func.now(),
            )
            db.add(registro)
        return registro
