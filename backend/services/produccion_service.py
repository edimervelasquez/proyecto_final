from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from backend.repositories.produccion_repository import ProduccionRepository


class ProduccionService:

    @staticmethod
    def registrar_orden(data, db: Session):
        insumos_receta = ProduccionRepository.obtener_insumos_receta(
            db, data.sku_prenda
        )
        if not insumos_receta:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No se encontró una Ficha Técnica registrada para el SKU: "
                    f"{data.sku_prenda}. Primero créala."
                ),
            )

        materiales = []
        for item in insumos_receta:
            material = ProduccionRepository.obtener_materia_prima(
                db, item.id_materiaPrima
            )
            if not material:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"El material con ID {item.id_materiaPrima} requerido "
                        "por la prenda no existe en el catálogo."
                    ),
                )

            cantidad_requerida = float(item.cantidad_estimada) * data.cantidad_a_producir
            if float(material.Cantidad_materiaPrima) < cantidad_requerida:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Falta material para la orden. El insumo "
                        f"'{material.nombre_material}' (ID: {material.id_materiaPrima}) "
                        f"tiene stock de {material.Cantidad_materiaPrima}, pero "
                        f"requieres {cantidad_requerida} para este lote."
                    ),
                )
            materiales.append((material, cantidad_requerida))

        try:
            for material, cantidad_requerida in materiales:
                material.Cantidad_materiaPrima = (
                    float(material.Cantidad_materiaPrima) - cantidad_requerida
                )

            id_usuario = data.id_usuario or data.id_empleado
            orden_data = {
                "id_area": data.id_area,
                "id_ingreso_insumos": 1,
                "fecha_recibido": func.current_date(),
                "fecha_entrega": data.fecha_entrega,
                "cantidad_recibida": data.cantidad_a_producir,
                "cantidad_entregada": 0,
            }
            nueva_orden = ProduccionRepository.registrar_orden(db, orden_data)
            if hasattr(nueva_orden, "id_usuario") and id_usuario:
                nueva_orden.id_usuario = id_usuario

            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return {
            "mensaje": (
                f"¡Orden de producción para {data.cantidad_a_producir} "
                f"unidades de {data.sku_prenda} iniciada con éxito!"
            ),
            "estado": "Materiales descontados del inventario correctamente.",
            "registrado_por_usuario": id_usuario,
        }

    @staticmethod
    def obtener_actividad_reciente(db: Session):
        try:
            ordenes = ProduccionRepository.obtener_actividad_reciente(db)
            return [
                {
                    "id_orden": orden.id_produccion,
                    "cantidad": orden.cantidad_recibida,
                    "fecha_recibido": str(orden.fecha_recibido),
                    "fecha_entrega": str(orden.fecha_entrega),
                    "id_area": orden.id_area,
                    "id_usuario": getattr(orden, "id_usuario", "No especificado"),
                }
                for orden in ordenes
            ]
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
