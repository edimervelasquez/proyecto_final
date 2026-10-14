from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models.models import (
    DetalleVenta,
    InventarioPrenda,
    MovimientoPrenda,
    ProductoComercial,
)
from backend.repositories.calidad_repository import CalidadRepository
from backend.repositories.comercial_repository import ComercialRepository


UBICACIONES = ("BODEGA_MAYORISTA", "BODEGA_LOCAL", "LOCAL")


class ComercialService:

    @staticmethod
    def actualizar_precios(sku: str, data, db: Session):
        try:
            producto = ComercialRepository.actualizar_precios(
                db,
                sku,
                data.precio_mayorista,
                data.precio_detal,
                data.costo_mano_obra,
            )
            if not producto:
                raise HTTPException(status_code=404, detail="Producto no encontrado.")
            db.commit()
            return {
                "mensaje": "Precios y costo actualizados.",
                "sku_prenda": sku,
            }
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def listar_productos(db: Session):
        productos = ComercialRepository.productos(db)
        stock = ComercialService._stock_index(db)
        return [
            {
                "sku_prenda": producto.sku_prenda,
                "nombre_producto": producto.nombre_producto,
                "descripcion": producto.descripcion,
                "precio_mayorista": float(producto.precio_mayorista),
                "precio_detal": float(producto.precio_detal),
                "costo_mano_obra": float(producto.costo_mano_obra),
                "existencias": {
                    ubicacion: stock.get((producto.sku_prenda, ubicacion), 0)
                    for ubicacion in UBICACIONES
                },
                "total_existencias": sum(
                    stock.get((producto.sku_prenda, ubicacion), 0)
                    for ubicacion in UBICACIONES
                ),
            }
            for producto in productos
        ]

    @staticmethod
    def listar_inventario(db: Session):
        productos = {
            producto.sku_prenda: producto
            for producto in ComercialRepository.productos(db)
        }
        return [
            {
                "sku_prenda": stock.sku_prenda,
                "nombre_producto": productos[stock.sku_prenda].nombre_producto
                if stock.sku_prenda in productos
                else stock.sku_prenda,
                "ubicacion": stock.ubicacion,
                "cantidad": stock.cantidad,
            }
            for stock in ComercialRepository.stocks(db)
        ]

    @staticmethod
    def listar_movimientos(db: Session):
        productos = {
            producto.sku_prenda: producto.nombre_producto
            for producto in ComercialRepository.productos(db)
        }
        return [
            {
                "id_movimiento": movimiento.id_movimiento,
                "sku_prenda": movimiento.sku_prenda,
                "producto": productos.get(
                    movimiento.sku_prenda, movimiento.sku_prenda
                ),
                "ubicacion": movimiento.ubicacion,
                "tipo": movimiento.tipo_movimiento,
                "cantidad": movimiento.cantidad,
                "referencia": movimiento.referencia,
                "registrado_por": empleado,
                "fecha": movimiento.fecha_movimiento.isoformat(),
            }
            for movimiento, empleado in ComercialRepository.movimientos(db)
        ]

    @staticmethod
    def _stock_index(db: Session):
        return {
            (stock.sku_prenda, stock.ubicacion): stock.cantidad
            for stock in ComercialRepository.stocks(db)
        }

    @staticmethod
    def _obtener_stock(db: Session, sku: str, ubicacion: str):
        stock = ComercialRepository.stock(db, sku, ubicacion, lock=True)
        if not stock:
            stock = ComercialRepository.crear_stock(db, sku, ubicacion)
        return stock

    @staticmethod
    def _registrar_movimiento(
        db: Session,
        *,
        sku: str,
        ubicacion: str,
        tipo: str,
        cantidad: int,
        costo: Decimal,
        id_usuario: int,
        referencia: str,
        grupo_traslado: str = None,
    ):
        ComercialRepository.movimiento(db, {
            "sku_prenda": sku,
            "ubicacion": ubicacion,
            "tipo_movimiento": tipo,
            "cantidad": cantidad,
            "costo_unitario": costo,
            "id_usuario": id_usuario,
            "referencia": referencia,
            "grupo_traslado": grupo_traslado,
            "fecha_movimiento": datetime.now(),
        })

    @staticmethod
    def registrar_aprobadas_de_orden(
        db: Session,
        id_produccion: int,
        cantidad: int,
        id_usuario: int,
    ):
        if cantidad <= 0:
            return
        destino = ComercialRepository.orden_comercial(db, id_produccion)
        if not destino:
            raise HTTPException(
                status_code=409,
                detail="La orden no tiene configurado el producto y canal de destino.",
            )
        orden = ComercialRepository.orden(db, id_produccion, lock=True)
        if not orden or orden.id_area is None:
            raise HTTPException(status_code=404, detail="Orden de producción no encontrada.")
        area = ComercialRepository.area(db, orden.id_area)
        if not area or area.nombre_area != "Calidad y Empaque":
            raise HTTPException(
                status_code=409,
                detail="Las prendas aprobadas solo ingresan al inventario desde Calidad y Empaque.",
            )
        ubicacion = (
            "BODEGA_MAYORISTA"
            if destino.canal_destino == "MAYORISTA"
            else "BODEGA_LOCAL"
        )
        stock = ComercialService._obtener_stock(db, destino.sku_prenda, ubicacion)
        stock.costo_promedio = (
            (
                Decimal(stock.cantidad) * Decimal(stock.costo_promedio)
                + Decimal(cantidad) * Decimal(destino.costo_unitario_estimado)
            )
            / Decimal(stock.cantidad + cantidad)
            if stock.cantidad + cantidad
            else Decimal(0)
        )
        stock.cantidad += cantidad
        ComercialService._registrar_movimiento(
            db,
            sku=destino.sku_prenda,
            ubicacion=ubicacion,
            tipo="PRODUCCION_APROBADA",
            cantidad=cantidad,
            costo=Decimal(destino.costo_unitario_estimado),
            id_usuario=id_usuario,
            referencia=f"OP-{id_produccion}",
        )

    @staticmethod
    def registrar_inventario_inicial(data, db: Session, id_usuario: int):
        if not ComercialRepository.producto(db, data.sku_prenda):
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        try:
            stock = ComercialRepository.stock(
                db, data.sku_prenda, data.ubicacion, lock=True
            )
            if (
                (stock and stock.cantidad != 0)
                or ComercialRepository.tiene_movimientos(
                    db, data.sku_prenda, data.ubicacion
                )
            ):
                raise HTTPException(
                    status_code=409,
                    detail="El inventario inicial solo puede registrarse una vez y antes de otros movimientos.",
                )
            stock = stock or ComercialRepository.crear_stock(
                db, data.sku_prenda, data.ubicacion
            )
            costo = Decimal(str(data.costo_unitario))
            stock.cantidad = data.cantidad
            stock.costo_promedio = costo
            ComercialService._registrar_movimiento(
                db,
                sku=data.sku_prenda,
                ubicacion=data.ubicacion,
                tipo="INVENTARIO_INICIAL",
                cantidad=data.cantidad,
                costo=costo,
                id_usuario=id_usuario,
                referencia="Carga inicial de existencias",
            )
            db.commit()
            return {
                "mensaje": "Inventario inicial registrado.",
                "sku_prenda": data.sku_prenda,
                "ubicacion": data.ubicacion,
                "cantidad": data.cantidad,
            }
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def trasladar(data, db: Session, id_usuario: int):
        if data.ubicacion_origen == data.ubicacion_destino:
            raise HTTPException(
                status_code=400,
                detail="El origen y el destino del traslado deben ser distintos.",
            )
        if not ComercialRepository.producto(db, data.sku_prenda):
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        try:
            origen = ComercialRepository.stock(
                db, data.sku_prenda, data.ubicacion_origen, lock=True
            )
            if not origen or origen.cantidad < data.cantidad:
                disponible = origen.cantidad if origen else 0
                raise HTTPException(
                    status_code=400,
                    detail=f"Existencia insuficiente en origen: hay {disponible}.",
                )
            destino = ComercialService._obtener_stock(
                db, data.sku_prenda, data.ubicacion_destino
            )
            cantidad_destino = destino.cantidad
            costo_traslado = Decimal(origen.costo_promedio)
            destino.costo_promedio = (
                (
                    Decimal(cantidad_destino) * Decimal(destino.costo_promedio)
                    + Decimal(data.cantidad) * costo_traslado
                )
                / Decimal(cantidad_destino + data.cantidad)
            )
            origen.cantidad -= data.cantidad
            destino.cantidad += data.cantidad
            grupo = str(uuid4())
            referencia = (
                f"{data.ubicacion_origen} -> {data.ubicacion_destino}"
            )
            ComercialService._registrar_movimiento(
                db,
                sku=data.sku_prenda,
                ubicacion=data.ubicacion_origen,
                tipo="TRASLADO_SALIDA",
                cantidad=-data.cantidad,
                costo=costo_traslado,
                id_usuario=id_usuario,
                referencia=referencia,
                grupo_traslado=grupo,
            )
            ComercialService._registrar_movimiento(
                db,
                sku=data.sku_prenda,
                ubicacion=data.ubicacion_destino,
                tipo="TRASLADO_ENTRADA",
                cantidad=data.cantidad,
                costo=costo_traslado,
                id_usuario=id_usuario,
                referencia=referencia,
                grupo_traslado=grupo,
            )
            db.commit()
            return {
                "mensaje": f"Traslado registrado: {data.cantidad} unidades.",
                "ubicacion_origen": data.ubicacion_origen,
                "ubicacion_destino": data.ubicacion_destino,
            }
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def registrar_venta(data, db: Session, id_usuario: int):
        ubicacion = "BODEGA_MAYORISTA" if data.canal == "MAYORISTA" else "LOCAL"
        try:
            cantidades = {}
            for item in data.detalles:
                sku = item.sku_prenda.strip()
                cantidades[sku] = cantidades.get(sku, 0) + item.cantidad

            lineas = []
            total = Decimal(0)
            for sku, cantidad in cantidades.items():
                producto = ComercialRepository.producto(db, sku)
                if not producto:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Producto {sku} no encontrado o inactivo.",
                    )
                precio = Decimal(
                    producto.precio_mayorista
                    if data.canal == "MAYORISTA"
                    else producto.precio_detal
                )
                if precio <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"El producto {sku} no tiene precio configurado para este canal.",
                    )
                stock = ComercialRepository.stock(
                    db, sku, ubicacion, lock=True
                )
                disponible = stock.cantidad if stock else 0
                if disponible < cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Stock insuficiente de {producto.nombre_producto} "
                            f"en {ubicacion}: hay {disponible}, solicitas {cantidad}."
                        ),
                    )
                costo = Decimal(stock.costo_promedio) if stock else Decimal(0)
                lineas.append((producto, stock, cantidad, precio, costo))
                total += precio * cantidad

            venta = ComercialRepository.crear_venta(
                db, data.canal, data.cliente.strip(), id_usuario
            )
            venta.total = total
            for producto, stock, cantidad, precio, costo in lineas:
                stock.cantidad -= cantidad
                ComercialRepository.crear_detalle_venta(db, {
                    "id_venta": venta.id_venta,
                    "sku_prenda": producto.sku_prenda,
                    "cantidad": cantidad,
                    "precio_unitario": precio,
                    "costo_unitario": costo,
                })
                ComercialService._registrar_movimiento(
                    db,
                    sku=producto.sku_prenda,
                    ubicacion=ubicacion,
                    tipo="VENTA",
                    cantidad=-cantidad,
                    costo=costo,
                    id_usuario=id_usuario,
                    referencia=f"VENTA-{venta.id_venta}",
                )
            db.commit()
            return {
                "id_venta": venta.id_venta,
                "canal": venta.canal,
                "total": float(total),
                "mensaje": "Venta registrada y existencias actualizadas.",
            }
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @staticmethod
    def listar_ventas(db: Session):
        resultado = []
        for venta, empleado in ComercialRepository.ventas(db):
            detalles = ComercialRepository.detalles_venta(db, venta.id_venta)
            resultado.append({
                "id_venta": venta.id_venta,
                "canal": venta.canal,
                "cliente": venta.cliente,
                "fecha_venta": venta.fecha_venta.isoformat(),
                "registrado_por": empleado,
                "total": float(venta.total),
                "detalles": [
                    {
                        "sku_prenda": detalle.sku_prenda,
                        "cantidad": detalle.cantidad,
                        "precio_unitario": float(detalle.precio_unitario),
                    }
                    for detalle in detalles
                ],
            })
        return resultado

    @staticmethod
    def resumen_financiero(db: Session):
        (
            total_ventas,
            ventas_mayoristas,
            ventas_detal,
            costo_vendido,
        ) = (
            Decimal(value)
            for value in ComercialRepository.resumen_ventas(db)
        )
        perdida_calidad = Decimal(
            CalidadRepository.obtener_perdida_estimada(db) or 0
        )

        margen = total_ventas - costo_vendido
        return {
            "ventas_totales": float(total_ventas),
            "ventas_mayoristas": float(ventas_mayoristas),
            "ventas_detal": float(ventas_detal),
            "costo_productos_vendidos": float(costo_vendido),
            "margen_bruto": float(margen),
            "perdida_estimada_calidad": float(perdida_calidad),
            "margen_despues_rechazos": float(margen - perdida_calidad),
            "nota": "Margen antes de gastos generales, impuestos y otros costos no registrados.",
        }
