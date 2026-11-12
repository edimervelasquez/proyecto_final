from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.repositories.comercial_repository import ComercialRepository
from backend.repositories.produccion_repository import ProduccionRepository


class TrazoService:
    @staticmethod
    def registrar_trazo(data, db: Session, id_usuario: int):
        try:
            ingreso = ProduccionRepository.obtener_ingreso(
                db,
                data.id_ingreso,
                lock=True,
            )
            if not ingreso:
                raise HTTPException(
                    status_code=404,
                    detail=f"No existe el ingreso de insumos {data.id_ingreso}.",
                )

            producto = ComercialRepository.producto(db, data.sku_prenda.strip())
            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"No existe la prenda {data.sku_prenda} o su ficha técnica."
                    ),
                )
            insumos_receta = ProduccionRepository.obtener_insumos_receta(
                db, producto.sku_prenda
            )
            cantidad_por_prenda = sum(
                (
                    Decimal(str(item.cantidad_estimada))
                    for item in insumos_receta
                    if item.id_materiaPrima == ingreso.id_materiaPrima
                ),
                Decimal("0"),
            )
            if cantidad_por_prenda == 0:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "El material del ingreso no hace parte de la ficha "
                        "técnica de esta prenda."
                    ),
                )
            cantidad_esperada = cantidad_por_prenda * data.cantidad_prendas
            if (
                abs(cantidad_esperada - data.cantidad_materia_prima)
                > Decimal("0.01")
            ):
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"La ficha requiere {cantidad_esperada} unidades de "
                        f"este material para {data.cantidad_prendas} prendas."
                    ),
                )

            cantidad_trazada_ingreso = sum(
                (
                    Decimal(trazo.cantidad_materia_prima)
                    for trazo in ProduccionRepository.trazos_por_ingreso(
                        db, ingreso.id_entrante
                    )
                ),
                Decimal("0"),
            )
            if (
                cantidad_trazada_ingreso + data.cantidad_materia_prima
                > Decimal(ingreso.cantidad_materia_prima)
            ):
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "La cantidad trazada supera la cantidad registrada "
                        "en el ingreso seleccionado."
                    ),
                )

            material = ProduccionRepository.obtener_materia_prima(
                db,
                ingreso.id_materiaPrima,
                lock=True,
            )
            if not material:
                raise HTTPException(
                    status_code=404,
                    detail="La materia prima asociada al ingreso no existe.",
                )
            cantidad_reservada = sum(
                (
                    Decimal(trazo.cantidad_materia_prima)
                    for trazo in
                    ProduccionRepository.trazos_pendientes_por_material(
                        db, ingreso.id_materiaPrima
                    )
                ),
                Decimal("0"),
            )
            cantidad_disponible = (
                Decimal(material.Cantidad_materiaPrima or 0)
                - cantidad_reservada
            )
            if data.cantidad_materia_prima > cantidad_disponible:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Solo hay {cantidad_disponible} unidades de "
                        f"{material.nombre_material} disponibles para trazar."
                    ),
                )

            trazo = ProduccionRepository.registrar_trazo(db, {
                "id_ingreso": ingreso.id_entrante,
                "sku_prenda": producto.sku_prenda,
                "cantidad_materia_prima": data.cantidad_materia_prima,
                "cantidad_prendas": data.cantidad_prendas,
                "observaciones": data.observaciones,
                "id_usuario": id_usuario,
            })
            db.commit()
            db.refresh(trazo)
            return TrazoService._serializar_trazo(
                trazo,
                ingreso.id_materiaPrima,
                material.nombre_material,
            )
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def listar_trazos(db: Session):
        return [
            TrazoService._serializar_trazo(trazo, id_material, nombre)
            for trazo, id_material, nombre in
            ProduccionRepository.listar_trazos(db)
        ]

    @staticmethod
    def _serializar_trazo(trazo, id_material: int, nombre_material: str):
        return {
            "id_trazo": trazo.id_trazo,
            "id_ingreso": trazo.id_ingreso,
            "id_materiaPrima": id_material,
            "nombre_material": nombre_material,
            "sku_prenda": trazo.sku_prenda,
            "id_produccion": trazo.id_produccion,
            "cantidad_materia_prima": trazo.cantidad_materia_prima,
            "cantidad_prendas": trazo.cantidad_prendas,
            "observaciones": trazo.observaciones,
            "id_usuario": trazo.id_usuario,
            "fecha_registro": trazo.fecha_registro,
        }
