from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.repositories.insumos_repository import InsumosRepository
from datetime import date

class InsumosService:

    @staticmethod
    def procesar_ingreso_insumo(data, db: Session):
        material = InsumosRepository.obtener_materia_prima(db, data.id_materiaPrima)
        if not material:
            raise HTTPException(status_code=404, detail="La materia prima especificada no existe en el catálogo.")

        try:
            current_cantidad = float(material.Cantidad_materiaPrima or 0)
            material.Cantidad_materiaPrima = current_cantidad + data.cantidad

            ingreso_dict = {
                "id_materiaPrima": data.id_materiaPrima,
                "cantidad_materia_prima": data.cantidad,
                "proveedor": data.proveedor,
                "costo_unitario": data.costo_unitario,
                "fecha_ingreso": data.fecha_ingreso if data.fecha_ingreso else date.today()
            }
            InsumosRepository.registrar_ingreso(db, ingreso_dict)
            db.commit()

            return {
                "mensaje": "Ingreso de materia prima registrado correctamente.",
                "nuevo_stock": material.Cantidad_materiaPrima
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def procesar_ficha_tecnica(data, db: Session):
        try:
            costo_total_insumos = 0.0
            detalles_guardados = []

            for insumo in data.insumos:
                ultimo_ingreso = InsumosRepository.obtener_ultimo_costo(db, insumo.id_materiaPrima)
                precio_unitario = float(ultimo_ingreso.costo_unitario) if ultimo_ingreso and ultimo_ingreso.costo_unitario else 5000.0

                costo_parcial = insumo.cantidad_estimada * precio_unitario
                costo_total_insumos += costo_parcial

                InsumosRepository.guardar_linea_ficha(db, data.sku_prenda, insumo.id_materiaPrima, insumo.cantidad_estimada)
                
                detalles_guardados.append({
                    "id_materiaPrima": insumo.id_materiaPrima,
                    "cantidad": insumo.cantidad_estimada,
                    "costo_estimado": costo_parcial
                })

            costo_fabricacion_base = costo_total_insumos + data.costo_mano_obra
            if costo_fabricacion_base <= 0:
                raise HTTPException(status_code=400, detail="El costo base de fabricación no puede ser cero.")

            db.commit()
            return {
                "mensaje": f"Ficha técnica para {data.sku_prenda} guardada con éxito.",
                "costo_materiales": costo_total_insumos,
                "costo_mano_obra": data.costo_mano_obra,
                "costo_total_fabricacion": costo_fabricacion_base,
                "detalles": detalles_guardados
            }
        except HTTPException as he:
            db.rollback()
            raise he
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))