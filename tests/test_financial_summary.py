import unittest
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.models import (
    Area,
    ControlCalidad,
    DetalleVenta,
    IngresoInsumos,
    MateriaPrima,
    OrdenComercial,
    Produccion,
    Rol,
    Usuario,
    Venta,
)
from backend.services.comercial_service import ComercialService


class FinancialSummaryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.db = self.session_factory()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_summary_aggregates_sales_cost_and_quality_loss(self):
        role = Rol(id_rol=1, nombre_rol="ADMINISTRADOR")
        self.db.add(role)
        self.db.flush()
        user = Usuario(
            empleado="Test",
            contrasenia="hash",
            correo="test@example.test",
            cedula_usuario="TEST",
            id_rol=role.id_rol,
            estado="ACTIVO",
        )
        material = MateriaPrima(
            nombre_material="Material de prueba",
            Cantidad_materiaPrima=10,
        )
        area = Area(nombre_area="Corte")
        self.db.add_all((user, material, area))
        self.db.flush()
        ingreso = IngresoInsumos(
            id_materiaPrima=material.id_materiaPrima,
            cantidad_materia_prima=10,
            proveedor="Prueba",
            costo_unitario=Decimal("5.00"),
            fecha_ingreso=date.today(),
        )
        self.db.add(ingreso)
        self.db.flush()
        order = Produccion(
            id_area=area.id_area,
            id_ingreso_insumos=ingreso.id_entrante,
            fecha_recibido=date.today(),
            fecha_entrega=date.today(),
            cantidad_recibida=10,
            cantidad_entregada=0,
        )
        self.db.add(order)
        self.db.flush()
        self.db.add(OrdenComercial(
            id_produccion=order.id_produccion,
            sku_prenda="TEST-SKU",
            canal_destino="DETAL",
            costo_unitario_estimado=Decimal("12.50"),
        ))
        self.db.add(ControlCalidad(
            id_produccion=order.id_produccion,
            id_usuario=user.id_usuario,
            cantidad_optima=7,
            cantidad_defectuosa=3,
            observaciones="Prueba",
        ))

        retail_sale = Venta(
            canal="DETAL",
            cliente="Cliente de prueba",
            id_usuario=user.id_usuario,
            total=Decimal("100.00"),
        )
        wholesale_sale = Venta(
            canal="MAYORISTA",
            cliente="Cliente mayorista de prueba",
            id_usuario=user.id_usuario,
            total=Decimal("80.00"),
        )
        self.db.add_all((retail_sale, wholesale_sale))
        self.db.flush()
        self.db.add_all((
            DetalleVenta(
                id_venta=retail_sale.id_venta,
                sku_prenda="TEST-SKU",
                cantidad=2,
                precio_unitario=Decimal("50.00"),
                costo_unitario=Decimal("20.00"),
            ),
            DetalleVenta(
                id_venta=retail_sale.id_venta,
                sku_prenda="TEST-SKU-2",
                cantidad=1,
                precio_unitario=Decimal("0.00"),
                costo_unitario=Decimal("10.00"),
            ),
            DetalleVenta(
                id_venta=wholesale_sale.id_venta,
                sku_prenda="TEST-SKU",
                cantidad=4,
                precio_unitario=Decimal("20.00"),
                costo_unitario=Decimal("15.00"),
            ),
        ))
        self.db.commit()

        summary = ComercialService.resumen_financiero(self.db)

        self.assertEqual(summary["ventas_totales"], 180.0)
        self.assertEqual(summary["ventas_detal"], 100.0)
        self.assertEqual(summary["ventas_mayoristas"], 80.0)
        self.assertEqual(summary["costo_productos_vendidos"], 110.0)
        self.assertEqual(summary["margen_bruto"], 70.0)
        self.assertEqual(summary["perdida_estimada_calidad"], 37.5)
        self.assertEqual(summary["margen_despues_rechazos"], 32.5)
        self.assertIn("nota", summary)

    def test_summary_is_zero_when_there_are_no_transactions(self):
        summary = ComercialService.resumen_financiero(self.db)

        self.assertEqual(summary["ventas_totales"], 0.0)
        self.assertEqual(summary["costo_productos_vendidos"], 0.0)
        self.assertEqual(summary["perdida_estimada_calidad"], 0.0)
        self.assertEqual(summary["margen_despues_rechazos"], 0.0)


if __name__ == "__main__":
    unittest.main()
