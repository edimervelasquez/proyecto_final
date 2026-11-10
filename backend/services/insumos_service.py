from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models.models import MateriaPrima
from backend.models.models import ProductoComercial
from backend.repositories.insumos_repository import InsumosRepository
from backend.repositories.trazabilidad_repository import TrazabilidadRepository


class InsumosService:

    @staticmethod
    def procesar_ingreso_insumo(data, db: Session, id_usuario: int):
        try:
            if data.id_materiaPrima is not None and data.nombre_material:
                raise HTTPException(
                    status_code=400,
                    detail="Selecciona un insumo existente o ingresa el nombre de uno nuevo, no ambos.",
                )
            if data.id_materiaPrima is not None:
                material = InsumosRepository.obtener_materia_prima(
                    db, data.id_materiaPrima, lock=True
                )
                if not material:
                    raise HTTPException(
                        status_code=404,
                        detail="La materia prima especificada no existe en el catálogo.",
                    )
            else:
                nombre_material = (data.nombre_material or "").strip()
                if not nombre_material:
                    raise HTTPException(
                        status_code=400,
                        detail="Selecciona un insumo o escribe el nombre del nuevo insumo.",
                    )
                if InsumosRepository.obtener_materia_por_nombre(
                    db, nombre_material
                ):
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "Ya existe un insumo con ese nombre. "
                            "Selecciónalo del catálogo."
                        ),
                    )
                material = MateriaPrima(
                    nombre_material=nombre_material,
                    Cantidad_materiaPrima=Decimal("0"),
                    stock_minimo=data.stock_minimo,
                )
                db.add(material)
                db.flush()

            ingreso = InsumosRepository.registrar_ingreso(db, {
                "id_materiaPrima": material.id_materiaPrima,
                "cantidad_materia_prima": data.cantidad,
                "proveedor": data.proveedor,
                "costo_unitario": data.costo_unitario,
                "fecha_ingreso": data.fecha_ingreso or date.today(),
            })
            material.Cantidad_materiaPrima = (
                Decimal(str(material.Cantidad_materiaPrima or 0))
                + data.cantidad
            )
            db.flush()
            InsumosRepository.registrar_movimiento(db, {
                "id_materiaPrima": material.id_materiaPrima,
                "tipo_movimiento": "ENTRADA",
                "cantidad": data.cantidad,
                "costo_unitario": data.costo_unitario or 0,
                "referencia": f"ING-{ingreso.id_entrante}",
                "id_usuario": id_usuario,
            })
            TrazabilidadRepository.registrar(
                db,
                "ingreso_insumo",
                ingreso.id_entrante,
                material.nombre_material,
                id_usuario,
                "Recepción de insumos",
                "Recibido",
            )
            db.commit()
            db.refresh(ingreso)
            db.refresh(material)
            return {
                "mensaje": "Ingreso de materia prima registrado correctamente.",
                "id_ingreso": ingreso.id_entrante,
                "id_materiaPrima": material.id_materiaPrima,
                "nombre_material": material.nombre_material,
                "nuevo_stock": float(material.Cantidad_materiaPrima),
            }
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def procesar_ficha_tecnica(data, db: Session, id_usuario: int):
        sku = data.sku_prenda.strip()
        if not sku:
            raise HTTPException(
                status_code=400,
                detail="El SKU de la ficha técnica es obligatorio.",
            )
        if InsumosRepository.existe_ficha(db, sku):
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe una ficha técnica para el SKU {sku}. Usa un SKU distinto.",
            )
        if db.query(ProductoComercial).filter_by(sku_prenda=sku).first():
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un producto comercial para el SKU {sku}.",
            )

        materiales = []
        for insumo in data.insumos:
            material = InsumosRepository.obtener_materia_prima(
                db, insumo.id_materiaPrima
            )
            if not material:
                raise HTTPException(
                    status_code=404,
                    detail=f"No existe el insumo con ID {insumo.id_materiaPrima}.",
                )
            materiales.append((insumo, material))

        try:
            ficha = ProductoComercial(
                sku_prenda=sku,
                nombre_producto=data.nombre_producto or sku,
                descripcion=data.descripcion,
                costo_mano_obra=data.costo_mano_obra or 0,
                precio_mayorista=data.precio_mayorista,
                precio_detal=data.precio_detal,
            )
            db.add(ficha)
            db.flush()

            costo_total_insumos = 0.0
            detalles_guardados = []
            for insumo, material in materiales:
                ultimo_ingreso = InsumosRepository.obtener_ultimo_costo(
                    db, insumo.id_materiaPrima
                )
                precio_unitario = (
                    float(ultimo_ingreso.costo_unitario)
                    if ultimo_ingreso and ultimo_ingreso.costo_unitario is not None
                    else 0.0
                )
                costo_parcial = float(insumo.cantidad_estimada) * precio_unitario
                costo_total_insumos += costo_parcial
                InsumosRepository.guardar_linea_ficha(
                    db,
                    sku,
                    insumo.id_materiaPrima,
                    insumo.cantidad_estimada,
                )
                detalles_guardados.append({
                    "id_materiaPrima": insumo.id_materiaPrima,
                    "nombre_material": material.nombre_material,
                    "cantidad": float(insumo.cantidad_estimada),
                    "costo_estimado": costo_parcial,
                })

            TrazabilidadRepository.registrar(
                db,
                "ficha_tecnica",
                sku,
                data.nombre_producto or sku,
                id_usuario,
                "Diseño y especificaciones",
                "Registrada",
                data.descripcion,
            )
            db.commit()
            db.refresh(ficha)
            mano_obra = data.costo_mano_obra or 0
            return {
                "mensaje": f"Ficha técnica para {sku} guardada con éxito.",
                "sku_prenda": sku,
                "costo_materiales": costo_total_insumos,
                "costo_mano_obra": mano_obra,
                "costo_total_fabricacion": costo_total_insumos + mano_obra,
                "precio_mayorista": data.precio_mayorista,
                "precio_detal": data.precio_detal,
                "detalles": detalles_guardados,
            }
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def listar_catalogo(db: Session):
        return [
            {
                "id_materiaPrima": material.id_materiaPrima,
                "nombre_material": material.nombre_material,
                "stock": material.Cantidad_materiaPrima,
                "stock_minimo": material.stock_minimo or 0,
                "alerta_bajo_stock": (
                    float(material.Cantidad_materiaPrima or 0)
                    <= float(material.stock_minimo or 0)
                ),
            }
            for material in InsumosRepository.obtener_materias_primas(db)
        ]

    @staticmethod
    def actualizar_stock_minimo(
        id_materia_prima: int, stock_minimo: int, db: Session
    ):
        try:
            material = InsumosRepository.actualizar_stock_minimo(
                db, id_materia_prima, stock_minimo
            )
            if not material:
                raise HTTPException(
                    status_code=404,
                    detail="El insumo indicado no existe en el catálogo.",
                )
            db.commit()
            return {
                "mensaje": "Stock mínimo actualizado correctamente.",
                "id_materiaPrima": material.id_materiaPrima,
                "stock_minimo": float(material.stock_minimo or 0),
            }
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def listar_alertas_stock(db: Session):
        return [
            {
                "id_materiaPrima": material.id_materiaPrima,
                "nombre_material": material.nombre_material,
                "stock": float(material.Cantidad_materiaPrima or 0),
                "stock_minimo": float(material.stock_minimo or 0),
                "estado": "Reponer",
            }
            for material in InsumosRepository.obtener_materias_primas(db)
            if float(material.Cantidad_materiaPrima or 0)
            <= float(material.stock_minimo or 0)
        ]

    @staticmethod
    def listar_movimientos(db: Session):
        movimientos = []
        for movimiento, nombre_material, empleado in (
            InsumosRepository.obtener_movimientos(db)
        ):
            movimientos.append({
                "id_movimiento": movimiento.id_movimiento,
                "referencia": movimiento.referencia
                or f"MOV-{movimiento.id_movimiento}",
                "insumo": nombre_material,
                "tipo_movimiento": movimiento.tipo_movimiento,
                "cantidad": float(movimiento.cantidad),
                "costo_unitario": float(movimiento.costo_unitario or 0),
                "registrado_por": empleado,
                "fecha_registro": (
                    movimiento.fecha_movimiento.isoformat()
                    if movimiento.fecha_movimiento
                    else None
                ),
                "proceso": (
                    "Producción"
                    if movimiento.tipo_movimiento == "CONSUMO_PRODUCCION"
                    else "Recepción de insumos"
                ),
                "estado": (
                    "Consumido"
                    if movimiento.tipo_movimiento == "CONSUMO_PRODUCCION"
                    else "Recibido"
                ),
            })
        return movimientos

    @staticmethod
    def listar_ingresos(db: Session):
        trazabilidad = TrazabilidadRepository.obtener_por_tipo(
            db, "ingreso_insumo"
        )
        materiales = {
            material.id_materiaPrima: material.nombre_material
            for material in InsumosRepository.obtener_materias_primas(db)
        }
        resultado = []
        for ingreso in InsumosRepository.obtener_ingresos(db):
            registro = trazabilidad.get(str(ingreso.id_entrante), {})
            resultado.append({
                "id_ingreso": ingreso.id_entrante,
                "insumo": materiales.get(
                    ingreso.id_materiaPrima, "Insumo desconocido"
                ),
                "cantidad": ingreso.cantidad_materia_prima,
                "proveedor": ingreso.proveedor,
                "costo_unitario": float(ingreso.costo_unitario)
                if ingreso.costo_unitario is not None
                else None,
                "fecha_ingreso": ingreso.fecha_ingreso.isoformat()
                if ingreso.fecha_ingreso
                else None,
                "registrado_por": registro.get("registrado_por", "No registrado"),
                "fecha_registro": registro.get("fecha_registro"),
                "proceso": registro.get(
                    "proceso", "Sin trazabilidad previa"
                ),
                "estado": registro.get("estado", "Sin trazabilidad previa"),
            })
        return resultado

    @staticmethod
    def listar_fichas(db: Session):
        trazabilidad = TrazabilidadRepository.obtener_por_tipo(
            db, "ficha_tecnica"
        )
        materiales = {
            material.id_materiaPrima: material.nombre_material
            for material in InsumosRepository.obtener_materias_primas(db)
        }
        lineas_por_sku = {}
        for linea in InsumosRepository.obtener_lineas_ficha(db):
            lineas_por_sku.setdefault(linea.sku_prenda, []).append({
                "insumo": materiales.get(
                    linea.id_materiaPrima, "Insumo desconocido"
                ),
                "cantidad_estimada": float(linea.cantidad_estimada),
            })

        resultado = []
        for sku, lineas in lineas_por_sku.items():
            registro = trazabilidad.get(sku, {})
            resultado.append({
                "sku_prenda": sku,
                "nombre_producto": registro.get("nombre_registro", sku),
                "descripcion": registro.get("descripcion"),
                "insumos": lineas,
                "registrado_por": registro.get("registrado_por", "No registrado"),
                "fecha_registro": registro.get("fecha_registro"),
                "proceso": registro.get(
                    "proceso", "Sin trazabilidad previa"
                ),
                "estado": registro.get("estado", "Sin trazabilidad previa"),
            })
        resultado.sort(
            key=lambda ficha: ficha["fecha_registro"] or "",
            reverse=True,
        )
        return resultado
