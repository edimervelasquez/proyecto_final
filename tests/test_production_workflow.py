import unittest
from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.models import (
    Area,
    FichaTecnicaInsumo,
    IngresoInsumos,
    InventarioPrenda,
    MateriaPrima,
    MovimientoInsumo,
    ProductoComercial,
    Rol,
    Usuario,
)
from backend.schemas.calidad_schema import ControlCalidadCreate
from backend.schemas.comercial_schema import (
    TrasladoPrendaCreate,
    VentaCreate,
    VentaDetalleCreate,
)
from backend.schemas.produccion_schema import (
    OrdenProduccionCreate,
    RetrasoProduccionCreate,
)
from backend.services.calidad_service import CalidadService
from backend.services.comercial_service import ComercialService
from backend.services.produccion_service import ProduccionService
from backend.services.retraso_service import RetrasoService


class ProductionWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
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

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_order_quality_inventory_transfer_and_sale(self):
        creation = ProduccionService.registrar_orden(
            OrdenProduccionCreate(
                id_area=self.areas[0].id_area,
                sku_prenda=self.product_sku,
                cantidad_a_producir=10,
                fecha_entrega=date.today() + timedelta(days=7),
                canal_destino="DETAL",
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

        for area in self.areas[1:]:
            ProduccionService.avanzar_etapa(
                order_id,
                area.id_area,
                self.db,
                self.user_id,
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
        )
        ComercialService.trasladar(transfer, self.db, self.user_id)
        sale = VentaCreate(
            canal="DETAL",
            cliente="Cliente de prueba",
            detalles=[
                VentaDetalleCreate(sku_prenda=self.product_sku, cantidad=2)
            ],
        )
        result = ComercialService.registrar_venta(sale, self.db, self.user_id)

        local_stock = self.db.query(InventarioPrenda).filter_by(
            sku_prenda=self.product_sku,
            ubicacion="LOCAL",
        ).one()
        self.assertEqual(local_stock.cantidad, 1)
        self.assertEqual(result["total"], 40.0)
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


if __name__ == "__main__":
    unittest.main()
