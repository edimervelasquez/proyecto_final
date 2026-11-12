from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.repositories.merma_repository import MermaRepository
from backend.repositories.trazabilidad_repository import TrazabilidadRepository
from backend.schemas.merma_schema import MermaCreate


class MermaService:

    @staticmethod
    def listar(db: Session):
        return [
            {
                "id_merma": merma.id_merma,
                "id_produccion": merma.id_produccion,
                "id_tipo_merma": merma.id_tipo_merma,
                "descripcion_tipo_merma": descripcion_tipo_merma,
                "cantidad_sobrante": merma.cantidad_sobrante,
                "fecha_registro": merma.fecha_registro,
            }
            for merma, descripcion_tipo_merma in MermaRepository.listar(db)
        ]

    @staticmethod
    def listar_tipos(db: Session):
        return MermaRepository.listar_tipos(db)

    @staticmethod
    def registrar(data: MermaCreate, db: Session):
        orden = MermaRepository.obtener_orden(db, data.id_produccion)
        if not orden:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No se encontró ninguna orden de producción con el "
                    f"ID {data.id_produccion}."
                ),
            )

        trazabilidad = TrazabilidadRepository.obtener_por_tipo(
            db, "orden_produccion"
        ).get(str(data.id_produccion))
        if trazabilidad and trazabilidad["estado"].strip().casefold() == "finalizada":
            raise HTTPException(
                status_code=409,
                detail="No se pueden registrar mermas en una orden finalizada.",
            )

        tipo = MermaRepository.obtener_tipo(db, data.id_tipo_merma)
        if not tipo:
            raise HTTPException(
                status_code=404,
                detail=f"No existe el tipo de merma con ID {data.id_tipo_merma}.",
            )

        try:
            merma = MermaRepository.registrar(
                db,
                {
                    "id_produccion": data.id_produccion,
                    "id_tipo_merma": data.id_tipo_merma,
                    "cantidad_sobrante": data.cantidad_sobrante,
                },
            )
            db.flush()
            resultado = {
                "id_merma": merma.id_merma,
                "id_produccion": merma.id_produccion,
                "id_tipo_merma": merma.id_tipo_merma,
                "descripcion_tipo_merma": tipo.descripcion_merma,
                "cantidad_sobrante": merma.cantidad_sobrante,
                "fecha_registro": merma.fecha_registro,
            }
            db.commit()
            return resultado
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="No se pudo registrar la merma.",
            ) from exc
