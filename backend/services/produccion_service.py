from datetime import date, datetime
from decimal import Decimal

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
        if area.nombre_area != ProduccionService.ETAPAS[0]:
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

        trazos, ingreso_referencia = ProduccionService._validar_trazos_orden(
            data,
            insumos_receta,
            db,
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
            trazos_pendientes = (
                ProduccionRepository.trazos_pendientes_por_material(
                    db, id_materia_prima
                )
            )
            cantidad_reservada_otros = sum(
                (
                    Decimal(trazo.cantidad_materia_prima)
                    for trazo in trazos_pendientes
                    if trazo.id_trazo not in (data.id_trazos or [])
                ),
                Decimal("0"),
            )
            cantidad_disponible = (
                Decimal(str(material.Cantidad_materiaPrima or 0))
                - cantidad_reservada_otros
            )
            if cantidad_disponible < Decimal(str(cantidad_requerida)):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Falta material para la orden. El insumo "
                        f"'{material.nombre_material}' tiene {cantidad_disponible} "
                        "unidades disponibles después de respetar los trazos "
                        "pendientes, pero requieres "
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

        if not ingreso_referencia:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Registra al menos un ingreso de insumos antes de crear "
                    "una orden de producción."
                ),
            )

        try:
            modelo = ProduccionRepository.obtener_o_crear_modelo(
                db,
                producto.nombre_producto,
                producto.descripcion,
            )
            for material, cantidad_requerida in materiales:
                material.Cantidad_materiaPrima = (
                    float(material.Cantidad_materiaPrima) - cantidad_requerida
                )

            nueva_orden = ProduccionRepository.registrar_orden(
                db,
                {
                    "id_modelo": modelo.id_modelo,
                    "id_area": data.id_area,
                    "id_ingreso_insumos": ingreso_referencia.id_entrante,
                    "fecha_recibido": date.today(),
                    "fecha_entrega": data.fecha_entrega,
                    "cantidad_recibida": data.cantidad_a_producir,
                    "cantidad_entregada": 0,
                    "estado_general": "EN_PROCESO",
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
            db.add(EtapaProduccion(
                id_produccion=nueva_orden.id_produccion,
                id_area_anterior=None,
                id_area_nueva=area.id_area,
                id_usuario=id_usuario,
                fecha_cambio=datetime.now(),
                estado="EN_PROCESO",
                observaciones=data.observaciones,
            ))
            for trazo in trazos:
                trazo.id_produccion = nueva_orden.id_produccion
            db.commit()
            db.refresh(nueva_orden)
            return {
                "mensaje": (
                    f"Orden de producción para {data.cantidad_a_producir} "
                    f"unidades de {data.sku_prenda} iniciada con éxito."
                ),
                "id_orden": nueva_orden.id_produccion,
                "estado": "En producción",
                "sku_prenda": data.sku_prenda,
                "cantidad": nueva_orden.cantidad_recibida,
                "etapa_inicial": area.nombre_area,
                "fecha_entrega": nueva_orden.fecha_entrega,
            }
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def _validar_trazos_orden(data, insumos_receta, db: Session):
        if not data.id_trazos:
            return [], ProduccionRepository.obtener_ultimo_ingreso(db)

        if len(set(data.id_trazos)) != len(data.id_trazos):
            raise HTTPException(
                status_code=422,
                detail="No repitas el mismo identificador de trazo.",
            )

        trazos = ProduccionRepository.obtener_trazos_por_ids(
            db,
            data.id_trazos,
            lock=True,
        )
        if len(trazos) != len(data.id_trazos):
            raise HTTPException(
                status_code=404,
                detail="Uno o más trazos no existen.",
            )

        cantidades_esperadas = {}
        for item in insumos_receta:
            id_material = item.id_materiaPrima
            cantidades_esperadas[id_material] = (
                cantidades_esperadas.get(id_material, Decimal("0"))
            + Decimal(str(item.cantidad_estimada))
                * data.cantidad_a_producir
            )

        cantidades_trazadas = {}
        ingresos = []
        for trazo in trazos:
            if trazo.id_produccion is not None:
                raise HTTPException(
                    status_code=409,
                    detail=f"El trazo {trazo.id_trazo} ya está asociado a una orden.",
                )
            if trazo.sku_prenda != data.sku_prenda:
                raise HTTPException(
                    status_code=409,
                    detail=f"El trazo {trazo.id_trazo} corresponde a otro SKU.",
                )
            if trazo.cantidad_prendas != data.cantidad_a_producir:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"El trazo {trazo.id_trazo} fue preparado para "
                        f"{trazo.cantidad_prendas} prendas, no para "
                        f"{data.cantidad_a_producir}."
                    ),
                )

            ingreso = ProduccionRepository.obtener_ingreso(db, trazo.id_ingreso)
            if not ingreso:
                raise HTTPException(
                    status_code=409,
                    detail=f"El ingreso del trazo {trazo.id_trazo} ya no existe.",
                )
            id_material = ingreso.id_materiaPrima
            cantidades_trazadas[id_material] = (
                cantidades_trazadas.get(id_material, Decimal("0"))
                + Decimal(trazo.cantidad_materia_prima)
            )
            ingresos.append(ingreso)

        ids_materiales = set(cantidades_esperadas) | set(cantidades_trazadas)
        for id_material in ids_materiales:
            esperado = cantidades_esperadas.get(id_material, Decimal("0"))
            trazado = cantidades_trazadas.get(id_material, Decimal("0"))
            if abs(esperado - trazado) > Decimal("0.01"):
                material = ProduccionRepository.obtener_materia_prima(
                    db, id_material
                )
                nombre = material.nombre_material if material else str(id_material)
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"El trazo del material '{nombre}' suma {trazado}; "
                        f"la ficha técnica requiere {esperado} para "
                        f"{data.cantidad_a_producir} prendas."
                    ),
                )

        return trazos, ingresos[0]

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
            cantidad_esperada = (
                cantidad_por_prenda * data.cantidad_prendas
            )
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
            return ProduccionService._serializar_trazo(
                trazo,
                ingreso.id_materiaPrima,
                material.nombre_material if material else "",
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
            ProduccionService._serializar_trazo(trazo, id_material, nombre)
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
    def listar_procesos(id_produccion: int, db: Session):
        if not ProduccionRepository.obtener_orden(db, id_produccion):
            raise HTTPException(
                status_code=404,
                detail="Orden de producción no encontrada.",
            )
        return [
            {
                "id_etapa": etapa.id_etapa,
                "id_produccion": etapa.id_produccion,
                "id_area": etapa.id_area_nueva,
                "etapa": nombre_area,
                "estado": etapa.estado,
                "fecha": etapa.fecha_cambio,
                "operario_id": etapa.id_usuario,
                "operario": empleado,
                "observaciones": etapa.observaciones,
            }
            for etapa, nombre_area, empleado
            in ProduccionRepository.obtener_procesos(db, id_produccion)
        ]

    @staticmethod
    def avanzar_etapa(
        id_produccion: int,
        id_area_destino: int,
        db: Session,
        id_usuario: int,
        observaciones: str | None = None,
    ):
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
            ahora = datetime.now()
            etapa_actual = ProduccionRepository.obtener_etapa_activa(
                db, id_produccion
            )
            if etapa_actual and etapa_actual.id_area_nueva != orden.id_area:
                raise HTTPException(
                    status_code=409,
                    detail="El historial de etapas no coincide con la etapa actual de la orden.",
                )
            if etapa_actual:
                etapa_actual.estado = "COMPLETADO"
                etapa_actual.observaciones = observaciones
                etapa_actual.id_usuario = id_usuario
            else:
                etapa_actual = EtapaProduccion(
                    id_produccion=id_produccion,
                    id_area_anterior=None,
                    id_area_nueva=orden.id_area,
                    id_usuario=id_usuario,
                    fecha_cambio=ahora,
                    estado="COMPLETADO",
                    observaciones=observaciones,
                )
                db.add(etapa_actual)

            etapa = EtapaProduccion(
                id_produccion=id_produccion,
                id_area_anterior=orden.id_area,
                id_area_nueva=id_area_destino,
                id_usuario=id_usuario,
                fecha_cambio=ahora,
                estado="EN_PROCESO",
            )
            db.add(etapa)
            db.flush()
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
                "id_etapa": etapa.id_etapa,
                "id_produccion": etapa.id_produccion,
                "id_area": etapa.id_area_nueva,
                "etapa": etapa_siguiente,
                "estado": etapa.estado,
                "fecha": etapa.fecha_cambio,
                "operario_id": id_usuario,
                "operario": ProduccionRepository.obtener_usuario(
                    db, id_usuario
                ).empleado,
                "observaciones": etapa.observaciones,
            }
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc
