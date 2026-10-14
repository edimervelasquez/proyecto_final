import unittest
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models.models import MovimientoInsumo, Rol, Usuario
from backend.schemas.insumos_schema import IngresoInsumoCreate
from backend.services.insumos_service import InsumosService


class InsumosMovementTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.db.add(Rol(id_rol=1, nombre_rol="ADMINISTRADOR"))
        self.db.flush()
        user = Usuario(
            empleado="Operador inventario",
            contrasenia="hash",
            correo="inventory@example.test",
            cedula_usuario="INV-TEST",
            id_rol=1,
            estado="ACTIVO",
        )
        self.db.add(user)
        self.db.commit()
        self.user_id = user.id_usuario

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_receipt_records_actor_date_quantity_and_low_stock(self):
        result = InsumosService.procesar_ingreso_insumo(
            IngresoInsumoCreate(
                nombre_material="Algodón de prueba",
                cantidad=4,
                proveedor="Proveedor de prueba",
                costo_unitario=Decimal("7.50"),
                fecha_ingreso=date.today(),
                stock_minimo=5,
            ),
            self.db,
            self.user_id,
        )

        movement = self.db.query(MovimientoInsumo).one()
        self.assertEqual(result["nuevo_stock"], 4)
        self.assertEqual(movement.tipo_movimiento, "ENTRADA")
        self.assertEqual(movement.cantidad, Decimal("4.00"))
        self.assertEqual(movement.referencia, f"ING-{result['id_ingreso']}")
        self.assertEqual(movement.id_usuario, self.user_id)
        self.assertIsNotNone(movement.fecha_movimiento)
        alerts = InsumosService.listar_alertas_stock(self.db)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["stock_minimo"], 5)

        history = InsumosService.listar_movimientos(self.db)
        self.assertEqual(history[0]["registrado_por"], "Operador inventario")
        self.assertEqual(history[0]["proceso"], "Recepción de insumos")
        self.assertIsNotNone(history[0]["fecha_registro"])

    def test_raising_stock_above_minimum_clears_alert(self):
        InsumosService.procesar_ingreso_insumo(
            IngresoInsumoCreate(
                nombre_material="Hilo de prueba",
                cantidad=4,
                stock_minimo=5,
            ),
            self.db,
            self.user_id,
        )
        catalog = InsumosService.listar_catalogo(self.db)
        InsumosService.actualizar_stock_minimo(
            catalog[0]["id_materiaPrima"], 3, self.db
        )

        self.assertEqual(InsumosService.listar_alertas_stock(self.db), [])


if __name__ == "__main__":
    unittest.main()
