from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.repositories.produccion_repository import ProduccionRepository
from backend.repositories.trazabilidad_repository import TrazabilidadRepository
from backend.repositories.comercial_repository import ComercialRepository
from backend.repositories.insumos_repository import InsumosRepository
from backend.models.models import EtapaProduccion
from backend.services.permisos_operativos import validar_usuario_operativo


class ProduccionService:
    ETAPAS = ("Corte", "Confección", "Estampado", "Calidad y Empaque")

    @staticmethod
    def registrar_orden(data, db: Session, id_usuario: int):
        area = ProduccionRepository.obtener_area(db, data.id_area)
        if not area:
            raise HTTPException(
                status_code=404,
                detail=f"No existe el área de producción con ID {data.id_area}.",
            )
        if area.nombre_area not in ProduccionService.ETAPAS:
            raise HTTPException(
                status_code=400,
                detail="La orden debe iniciar en el área Corte.",
            )
        if data.fecha_entrega < date.today():
            raise HTTPException(
                status_code=400,
                detail="La fecha de entrega no puede estar en el pasado.",
            )

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
        producto = ComercialRepository.producto(db, data.sku_prenda)
        if not producto:
            raise HTTPException(
                status_code=409,
                detail="Completa la ficha con precios mayorista y detal antes de producir.",
            )

        cantidades_requeridas = {}
        for item in insumos_receta:
            cantidades_requeridas[item.id_materiaPrima] = (
                cantidades_requeridas.get(item.id_materiaPrima, 0)
                + float(item.cantidad_estimada) * data.cantidad_a_producir
            )

        materiales = []
        costo_unitario_estimado = float(producto.costo_mano_obra or 0)
        for id_materia_prima, cantidad_requerida in cantidades_requeridas.items():
            material = ProduccionRepository.obtener_materia_prima(
                db, id_materia_prima, lock=True
            )
            if not material:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"El material con ID {id_materia_prima} requerido "
                        "por la ficha técnica no existe en el catálogo."
                    ),
                )
            if float(material.Cantidad_materiaPrima) < cantidad_requerida:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Falta material para la orden. El insumo "
                        f"'{material.nombre_material}' tiene stock de "
                        f"{material.Cantidad_materiaPrima}, pero requieres "
                        f"{cantidad_requerida} para este lote."
                    ),
                )
            materiales.append((material, cantidad_requerida))
            costo_unitario_estimado += (
                float(cantidad_requerida)
                / data.cantidad_a_producir
                * InsumosRepository.obtener_costo_unitario_actual(
                    db, id_materia_prima
                )
            )

        ingreso_referencia = ProduccionRepository.obtener_ultimo_ingreso(db)
        if not ingreso_referencia:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Registra al menos un ingreso de insumos antes de crear "
                    "una orden de producción."
                ),
            )

        try:
            for material, cantidad_requerida in materiales:
                material.Cantidad_materiaPrima = (
                    float(material.Cantidad_materiaPrima) - cantidad_requerida
                )

            nueva_orden = ProduccionRepository.registrar_orden(
                db,
                {
                    "id_area": data.id_area,
                    "id_ingreso_insumos": ingreso_referencia.id_entrante,
                    "fecha_recibido": date.today(),
                    "fecha_entrega": data.fecha_entrega,
                    "cantidad_recibida": data.cantidad_a_producir,
                    "cantidad_entregada": 0,
                },
            )
            db.flush()
            for material, cantidad_requerida in materiales:
                InsumosRepository.registrar_movimiento(db, {
                    "id_materiaPrima": material.id_materiaPrima,
                    "tipo_movimiento": "CONSUMO_PRODUCCION",
                    "cantidad": -cantidad_requerida,
                    "costo_unitario": InsumosRepository.obtener_costo_unitario_actual(
                        db, material.id_materiaPrima
                    ),
                    "referencia": f"OP-{nueva_orden.id_produccion}",
                    "id_produccion": nueva_orden.id_produccion,
                    "id_usuario": id_usuario,
                })
            ComercialRepository.guardar_orden_comercial(db, {
                "id_produccion": nueva_orden.id_produccion,
                "sku_prenda": data.sku_prenda,
                "canal_destino": data.canal_destino,
                "costo_unitario_estimado": costo_unitario_estimado,
            })
            TrazabilidadRepository.registrar(
                db,
                "orden_produccion",
                nueva_orden.id_produccion,
                f"OP-{nueva_orden.id_produccion}: {data.sku_prenda}",
                id_usuario,
                area.nombre_area or "Producción",
                "En producción",
            )
            db.commit()
            return {
                "mensaje": (
                    f"Orden de producción para {data.cantidad_a_producir} "
                    f"unidades de {data.sku_prenda} iniciada con éxito."
                ),
                "id_orden": nueva_orden.id_produccion,
                "estado": "En producción",
            }
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def obtener_actividad_reciente(db: Session):
        return ProduccionService.listar_ordenes(db, limite=10)

    @staticmethod
    def listar_ordenes(db: Session, limite: int = 100):
        trazabilidad = TrazabilidadRepository.obtener_por_tipo(
            db, "orden_produccion"
        )
        areas = {
            area.id_area: area.nombre_area
            for area in ProduccionRepository.obtener_areas(db)
        }
        retrasos_abiertos = {
            retraso.id_produccion: retraso
            for retraso in ProduccionRepository.obtener_retrasos_abiertos(db)
        }
        resultado = []
        for orden in ProduccionRepository.obtener_ordenes(db, limite):
            registro = trazabilidad.get(str(orden.id_produccion), {})
            sku = registro.get("nombre_registro", "").split(": ", 1)
            try:
                indice_etapa = ProduccionService.ETAPAS.index(
                    areas.get(orden.id_area, "")
                )
                siguiente_etapa = (
                    ProduccionService.ETAPAS[indice_etapa + 1]
                    if indice_etapa < len(ProduccionService.ETAPAS) - 1
                    else None
                )
            except ValueError:
                siguiente_etapa = None
            id_area_siguiente = next(
                (
                    area.id_area
                    for area in ProduccionRepository.obtener_areas(db)
                    if area.nombre_area == siguiente_etapa
                ),
                None,
            )
            resultado.append({
                "id_orden": orden.id_produccion,
                "sku_prenda": sku[1] if len(sku) > 1 else "No especificado",
                "cantidad": orden.cantidad_recibida,
                "cantidad_entregada": orden.cantidad_entregada or 0,
                "area": areas.get(orden.id_area, f"Área {orden.id_area}"),
                "fecha_recibido": orden.fecha_recibido.isoformat()
                if orden.fecha_recibido
                else None,
                "fecha_entrega": orden.fecha_entrega.isoformat()
                if orden.fecha_entrega
                else None,
                "registrado_por": registro.get("registrado_por", "No registrado"),
                "fecha_registro": registro.get("fecha_registro"),
                "proceso": registro.get(
                    "proceso", "Sin trazabilidad previa"
                ),
                "estado": registro.get(
                    "estado", "Sin trazabilidad previa"
                ),
                "retraso_abierto": orden.id_produccion in retrasos_abiertos,
                "motivo_retraso": (
                    retrasos_abiertos[orden.id_produccion].motivo
                    if orden.id_produccion in retrasos_abiertos
                    else None
                ),
                "siguiente_etapa": siguiente_etapa,
                "id_area_siguiente": id_area_siguiente,
            })
        return resultado

    @staticmethod
    def listar_areas(db: Session):
        return [
            {"id_area": area.id_area, "nombre_area": area.nombre_area}
            for area in ProduccionRepository.obtener_areas(db)
        ]

    @staticmethod
    def crear_area(data, db: Session):
        nombre = data.nombre_area.strip()
        if not nombre:
            raise HTTPException(
                status_code=400,
                detail="El nombre del área es obligatorio.",
            )
        if ProduccionRepository.obtener_area_por_nombre(db, nombre):
            raise HTTPException(
                status_code=409,
                detail="Ya existe un área de producción con ese nombre.",
            )
        try:
            area = ProduccionRepository.crear_area(db, nombre)
            db.commit()
            return {"id_area": area.id_area, "nombre_area": area.nombre_area}
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def avanzar_etapa(id_produccion: int, id_area_destino: int, db: Session, id_usuario: int):
        validar_usuario_operativo(db, id_usuario)
        orden = ProduccionRepository.obtener_orden_para_actualizar(
            db, id_produccion
        )
        if not orden:
            raise HTTPException(status_code=404, detail="Orden de producción no encontrada.")
        if ProduccionRepository.obtener_retraso_abierto(db, id_produccion):
            raise HTTPException(
                status_code=409,
                detail="Reanuda el retraso antes de avanzar la orden.",
            )
        area_actual = ProduccionRepository.obtener_area(db, orden.id_area)
        area_destino = ProduccionRepository.obtener_area(db, id_area_destino)
        if not area_actual or not area_destino:
            raise HTTPException(status_code=404, detail="Área de producción no encontrada.")
        try:
            posicion = ProduccionService.ETAPAS.index(area_actual.nombre_area)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="La orden no está en una etapa estándar de producción.",
            ) from exc
        if posicion >= len(ProduccionService.ETAPAS) - 1:
            raise HTTPException(
                status_code=409,
                detail="La orden ya está en Calidad y Empaque.",
            )
        etapa_siguiente = ProduccionService.ETAPAS[posicion + 1]
        if area_destino.nombre_area != etapa_siguiente:
            raise HTTPException(
                status_code=400,
                detail=f"La siguiente etapa de esta orden es {etapa_siguiente}.",
            )
        try:
            etapa = EtapaProduccion(
                id_produccion=id_produccion,
                id_area_anterior=orden.id_area,
                id_area_nueva=id_area_destino,
                id_usuario=id_usuario,
                fecha_cambio=datetime.now(),
            )
            db.add(etapa)
            orden.id_area = id_area_destino
            TrazabilidadRepository.actualizar_estado(
                db,
                "orden_produccion",
                id_produccion,
                f"En {etapa_siguiente}",
                etapa_siguiente,
                id_usuario,
                crear_si_no_existe=True,
            )
            db.commit()
            return {
                "mensaje": f"Orden OP-{id_produccion} avanzó a {etapa_siguiente}.",
                "proceso": etapa_siguiente,
                "estado": f"En {etapa_siguiente}",
            }
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc
