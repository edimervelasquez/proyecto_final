import unittest
from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.models import (
    Area,
    EtapaProduccion,
    DetalleVenta,
    FichaTecnicaInsumo,
    IngresoInsumos,
    InventarioPrenda,
    MateriaPrima,
    MovimientoInsumo,
    MovimientoPrenda,
    ProductoComercial,
    Produccion,
    Rol,
    TrazoProduccion,
    Usuario,
)
from backend.schemas.calidad_schema import ControlCalidadCreate
from backend.schemas.comercial_schema import (
    PedidoCreate,
    PedidoDetalleCreate,
    TrasladoPrendaCreate,
    VentaCreate,
    VentaDetalleCreate,
)
from backend.schemas.produccion_schema import (
    OrdenProduccionCreate,
    RetrasoProduccionCreate,
    TrazoProduccionCreate,
)
from backend.schemas.insumos_schema import DetalleInsumoFicha, FichaTecnicaCreate
from backend.repositories.comercial_repository import ComercialRepository
from backend.services.calidad_service import CalidadService
from backend.services.comercial_service import ComercialService
from backend.services.insumos_service import InsumosService
from backend.services.produccion_service import ProduccionService
from backend.services.retraso_service import RetrasoService


class ProductionWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        event.listen(
            self.engine,
            "connect",
            lambda connection, _: connection.execute("PRAGMA foreign_keys=ON"),
        )
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

        role = Rol(id_rol=1, nombre_rol="ADMINISTRADOR")
        self.db.add(role)
        self.db.flush()
        user = Usuario(
            empleado="Operador de prueba",
            contrasenia="hash",
            correo="operator@example.test",
            cedula_usuario="OP-TEST",
            id_rol=role.id_rol,
            estado="ACTIVO",
        )
        material = MateriaPrima(
            nombre_material="Tela de prueba",
            Cantidad_materiaPrima=100,
        )
        self.db.add_all((user, material))
        self.db.flush()

        ingreso = IngresoInsumos(
            id_materiaPrima=material.id_materiaPrima,
            cantidad_materia_prima=100,
            proveedor="Proveedor de prueba",
            costo_unitario=Decimal("5.00"),
            fecha_ingreso=date.today(),
        )
        self.db.add(ingreso)
        areas = [Area(nombre_area=name) for name in ProduccionService.ETAPAS]
        product = ProductoComercial(
            sku_prenda="WORKFLOW-TEST",
            nombre_producto="Prenda de prueba",
            costo_mano_obra=Decimal("2.00"),
            precio_mayorista=Decimal("12.00"),
            precio_detal=Decimal("20.00"),
            activo=1,
        )
        self.db.add_all((*areas, product))
        self.db.flush()
        self.db.add(FichaTecnicaInsumo(
            sku_prenda=product.sku_prenda,
            id_materiaPrima=material.id_materiaPrima,
            cantidad_estimada=Decimal("1.00"),
        ))
        self.db.commit()

        self.user_id = user.id_usuario
        self.product_sku = product.sku_prenda
        self.areas = areas
        self.ingreso_id = ingreso.id_entrante

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_creating_technical_sheet_persists_product_before_sku_foreign_key(self):
        response = InsumosService.procesar_ficha_tecnica(
            FichaTecnicaCreate(
                sku_prenda="NEW-WORKFLOW-TEST",
                nombre_producto="Nueva prenda",
                insumos=[
                    DetalleInsumoFicha(
                        id_materiaPrima=1,
                        cantidad_estimada=1,
                    )
                ],
                precio_mayorista=Decimal("15.00"),
                precio_detal=Decimal("25.00"),
            ),
            self.db,
            self.user_id,
        )

        self.assertEqual(response["sku_prenda"], "NEW-WORKFLOW-TEST")
        ficha_line = self.db.query(FichaTecnicaInsumo).filter_by(
            sku_prenda="NEW-WORKFLOW-TEST"
        ).one()
        self.assertEqual(ficha_line.id_materiaPrima, 1)

    def test_order_quality_inventory_transfer_and_sale(self):
        creation = ProduccionService.registrar_orden(
            OrdenProduccionCreate(
                id_area=self.areas[0].id_area,
                sku_prenda=self.product_sku,
                cantidad_a_producir=10,
                fecha_entrega=date.today() + timedelta(days=7),
                canal_destino="DETAL",
                observaciones="Orden preparada.",
            ),
            self.db,
            self.user_id,
        )
        order_id = creation["id_orden"]
        material_movement = self.db.query(MovimientoInsumo).filter_by(
            id_produccion=order_id,
            tipo_movimiento="CONSUMO_PRODUCCION",
        ).one()
        self.assertEqual(material_movement.cantidad, Decimal("-10.00"))
        self.assertEqual(material_movement.referencia, f"OP-{order_id}")
        self.assertEqual(material_movement.id_usuario, self.user_id)
        initial_stage = self.db.query(EtapaProduccion).filter_by(
            id_produccion=order_id
        ).one()
        self.assertEqual(initial_stage.id_area_nueva, self.areas[0].id_area)
        self.assertEqual(initial_stage.estado, "EN_PROCESO")
        self.assertEqual(initial_stage.observaciones, "Orden preparada.")

        delay = RetrasoService.registrar_retraso(
            order_id,
            RetrasoProduccionCreate(
                motivo="Falta de materia prima",
                detalle="Prueba automatizada",
            ),
            self.db,
            self.user_id,
        )
        with self.assertRaises(HTTPException) as paused_order:
            ProduccionService.avanzar_etapa(
                order_id,
                self.areas[1].id_area,
                self.db,
                self.user_id,
            )
        self.assertEqual(paused_order.exception.status_code, 409)
        resumed = RetrasoService.reanudar_produccion(
            delay["id_retraso"],
            self.db,
            self.user_id,
        )
        self.assertGreaterEqual(resumed["minutos_detenida"], 0)
        retrasos = RetrasoService.listar_retrasos(order_id, self.db)
        self.assertFalse(retrasos[0]["abierto"])

        with self.assertRaises(HTTPException) as invalid_transition:
            ProduccionService.avanzar_etapa(
                order_id,
                self.areas[2].id_area,
                self.db,
                self.user_id,
            )
        self.assertEqual(invalid_transition.exception.status_code, 400)

        for index, area in enumerate(self.areas[1:], start=1):
            ProduccionService.avanzar_etapa(
                order_id,
                area.id_area,
                self.db,
                self.user_id,
                f"{ProduccionService.ETAPAS[index - 1]} completada.",
            )
        stages_before_quality = (
            self.db.query(EtapaProduccion)
            .filter_by(id_produccion=order_id)
            .order_by(EtapaProduccion.id_etapa)
            .all()
        )
        self.assertEqual(
            [stage.estado for stage in stages_before_quality],
            ["COMPLETADO", "COMPLETADO", "COMPLETADO", "EN_PROCESO"],
        )
        self.assertEqual(
            stages_before_quality[0].observaciones,
            "Corte completada.",
        )
        CalidadService.registrar_control(
            ControlCalidadCreate(
                id_produccion=order_id,
                cantidad_optima=7,
                cantidad_defectuosa=3,
                observaciones="Prueba automatizada",
            ),
            self.db,
            self.user_id,
        )
        self.db.refresh(stages_before_quality[-1])
        self.assertEqual(stages_before_quality[-1].estado, "COMPLETADO")
        self.assertIn("Inspección finalizada", stages_before_quality[-1].observaciones)

        approved_stock = self.db.query(InventarioPrenda).filter_by(
            sku_prenda=self.product_sku,
            ubicacion="BODEGA_LOCAL",
        ).one()
        self.assertEqual(approved_stock.cantidad, 7)

        transfer = TrasladoPrendaCreate(
            sku_prenda=self.product_sku,
            ubicacion_origen="BODEGA_LOCAL",
            ubicacion_destino="LOCAL",
            cantidad=3,
            id_produccion=order_id,
        )
        ComercialService.trasladar(transfer, self.db, self.user_id)
        sale = PedidoCreate(
            canal="DETAL",
            cliente="Cliente de prueba",
            detalles=[
                PedidoDetalleCreate(
                    sku_prenda=self.product_sku,
                    cantidad=2,
                    id_produccion=order_id,
                )
            ],
        )
        result = ComercialService.registrar_venta(
            sale,
            self.db,
            self.user_id,
            require_production_lot=True,
        )

        local_stock = self.db.query(InventarioPrenda).filter_by(
            sku_prenda=self.product_sku,
            ubicacion="LOCAL",
        ).one()
        self.assertEqual(local_stock.cantidad, 1)
        self.assertEqual(result["total"], 40.0)
        sale_detail = self.db.query(DetalleVenta).filter_by(
            id_venta=result["id_venta"]
        ).one()
        self.assertEqual(sale_detail.id_produccion, order_id)
        sale_movement = self.db.query(MovimientoPrenda).filter_by(
            referencia=f"VENTA-{result['id_venta']}"
        ).one()
        self.assertEqual(sale_movement.id_produccion, order_id)
        self.assertEqual(
            ComercialRepository.saldo_lote(
                self.db, self.product_sku, order_id, "LOCAL"
            ),
            1,
        )
        summary = ComercialService.resumen_financiero(self.db)
        self.assertEqual(summary["ventas_detal"], 40.0)
        self.assertEqual(summary["perdida_estimada_calidad"], 21.0)

        excessive_sale = VentaCreate(
            canal="DETAL",
            cliente="Venta sin existencias",
            detalles=[
                VentaDetalleCreate(sku_prenda=self.product_sku, cantidad=2)
            ],
        )
        with self.assertRaises(HTTPException) as insufficient_stock:
            ComercialService.registrar_venta(
                excessive_sale,
                self.db,
                self.user_id,
            )
        self.assertEqual(insufficient_stock.exception.status_code, 400)
        self.db.refresh(local_stock)
        self.assertEqual(local_stock.cantidad, 1)

        missing_lot = VentaCreate(
            canal="DETAL",
            cliente="Pedido sin lote",
            detalles=[
                VentaDetalleCreate(sku_prenda=self.product_sku, cantidad=1)
            ],
        )
        with self.assertRaises(HTTPException) as required_lot:
            ComercialService.registrar_venta(
                missing_lot,
                self.db,
                self.user_id,
                require_production_lot=True,
            )
        self.assertEqual(required_lot.exception.status_code, 422)

        wrong_order = PedidoCreate(
            canal="DETAL",
            cliente="Pedido de otro lote",
            detalles=[
                PedidoDetalleCreate(
                    sku_prenda=self.product_sku,
                    cantidad=1,
                    id_produccion=99999,
                )
            ],
        )
        with self.assertRaises(HTTPException) as missing_order:
            ComercialService.registrar_venta(
                wrong_order,
                self.db,
                self.user_id,
                require_production_lot=True,
            )
        self.assertEqual(missing_order.exception.status_code, 404)

    def test_trace_uses_specific_receipt_and_is_linked_to_production_order(self):
        trace = ProduccionService.registrar_trazo(
            TrazoProduccionCreate(
                id_ingreso=self.ingreso_id,
                sku_prenda=self.product_sku,
                cantidad_materia_prima=Decimal("10.00"),
                cantidad_prendas=10,
                observaciones="Tela reservada para este lote.",
            ),
            self.db,
            self.user_id,
        )
        self.assertEqual(trace["id_ingreso"], self.ingreso_id)
        self.assertEqual(trace["id_materiaPrima"], 1)
        self.assertEqual(trace["sku_prenda"], self.product_sku)
        self.assertIsNone(trace["id_produccion"])

        order = ProduccionService.registrar_orden(
            OrdenProduccionCreate(
                id_area=self.areas[0].id_area,
                sku_prenda=self.product_sku,
                cantidad_a_producir=10,
                fecha_entrega=date.today() + timedelta(days=5),
                canal_destino="DETAL",
                id_trazos=[trace["id_trazo"]],
            ),
            self.db,
            self.user_id,
        )

        persisted_trace = self.db.query(TrazoProduccion).filter_by(
            id_trazo=trace["id_trazo"]
        ).one()
        production_order = self.db.query(Produccion).filter_by(
            id_produccion=order["id_orden"]
        ).one()
        movement = self.db.query(MovimientoInsumo).filter_by(
            id_produccion=order["id_orden"],
            tipo_movimiento="CONSUMO_PRODUCCION",
        ).one()
        self.assertEqual(persisted_trace.id_produccion, order["id_orden"])
        self.assertEqual(production_order.id_ingreso_insumos, self.ingreso_id)
        self.assertEqual(movement.cantidad, Decimal("-10.00"))

    def test_trace_rejects_receipt_not_used_by_the_technical_sheet(self):
        material = MateriaPrima(
            nombre_material="Hilo alterno",
            Cantidad_materiaPrima=20,
        )
        self.db.add(material)
        self.db.flush()
        unrelated_receipt = IngresoInsumos(
            id_materiaPrima=material.id_materiaPrima,
            cantidad_materia_prima=20,
            proveedor="Alterno",
            costo_unitario=Decimal("1.00"),
            fecha_ingreso=date.today(),
        )
        self.db.add(unrelated_receipt)
        self.db.commit()

        with self.assertRaises(HTTPException) as invalid_material:
            ProduccionService.registrar_trazo(
                TrazoProduccionCreate(
                    id_ingreso=unrelated_receipt.id_entrante,
                    sku_prenda=self.product_sku,
                    cantidad_materia_prima=Decimal("1.00"),
                    cantidad_prendas=1,
                ),
                self.db,
                self.user_id,
            )
        self.assertEqual(invalid_material.exception.status_code, 409)

    def test_trace_must_match_recipe_and_reserves_stock_for_its_order(self):
        with self.assertRaises(HTTPException) as wrong_quantity:
            ProduccionService.registrar_trazo(
                TrazoProduccionCreate(
                    id_ingreso=self.ingreso_id,
                    sku_prenda=self.product_sku,
                    cantidad_materia_prima=Decimal("9.00"),
                    cantidad_prendas=10,
                ),
                self.db,
                self.user_id,
            )
        self.assertEqual(wrong_quantity.exception.status_code, 409)

        ProduccionService.registrar_trazo(
            TrazoProduccionCreate(
                id_ingreso=self.ingreso_id,
                sku_prenda=self.product_sku,
                cantidad_materia_prima=Decimal("10.00"),
                cantidad_prendas=10,
            ),
            self.db,
            self.user_id,
        )
        with self.assertRaises(HTTPException) as reserved_stock:
            ProduccionService.registrar_orden(
                OrdenProduccionCreate(
                    id_area=self.areas[0].id_area,
                    sku_prenda=self.product_sku,
                    cantidad_a_producir=95,
                    fecha_entrega=date.today() + timedelta(days=5),
                    canal_destino="DETAL",
                ),
                self.db,
                self.user_id,
            )
        self.assertEqual(reserved_stock.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
