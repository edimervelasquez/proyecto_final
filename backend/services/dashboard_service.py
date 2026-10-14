from sqlalchemy.orm import Session

from backend.repositories.dashboard_repository import DashboardRepository
from backend.repositories.trazabilidad_repository import TrazabilidadRepository
from backend.services.calidad_service import CalidadService
from backend.services.produccion_service import ProduccionService
from backend.services.retraso_service import RetrasoService
from backend.services.comercial_service import ComercialService
from backend.services.insumos_service import InsumosService


class DashboardService:

    @staticmethod
    def obtener_rendimiento(db: Session):
        ordenes = DashboardRepository.obtener_ordenes_produccion(db)
        controles = CalidadService.obtener_resumen(db)
        total_recibido = sum(orden.cantidad_recibida for orden in ordenes)
        total_optimo = sum(orden.cantidad_entregada or 0 for orden in ordenes)
        total_defectuoso = controles["total_defectuoso"]
        return {
            "total_recibido": total_recibido,
            "total_optimo": controles["total_optimo"],
            "total_defectuoso": total_defectuoso,
            "eficiencia": controles["aprobacion_calidad"],
        }

    @staticmethod
    def obtener_resumen(db: Session):
        materiales = DashboardRepository.obtener_materias_primas(db)
        ingresos = DashboardRepository.obtener_ingresos(db)
        ordenes = DashboardRepository.obtener_ordenes_produccion(db)
        estado_ordenes = TrazabilidadRepository.obtener_por_tipo(
            db, "orden_produccion"
        )
        resumen_calidad = CalidadService.obtener_resumen(db)
        resumen_retrasos = RetrasoService.resumen_retrasos(db)
        finanzas = ComercialService.resumen_financiero(db)
        alertas_insumos = InsumosService.listar_alertas_stock(db)
        total_stock = sum(material.Cantidad_materiaPrima or 0 for material in materiales)
        ordenes_activas = sum(
            1
            for orden in ordenes
            if estado_ordenes.get(str(orden.id_produccion), {}).get("estado")
            != "Finalizada"
            and (orden.cantidad_entregada or 0) < orden.cantidad_recibida
        )
        valor_insumos = sum(
            float(ingreso.cantidad_materia_prima)
            * float(ingreso.costo_unitario or 0)
            for ingreso in ingresos
        )
        return {
            "unidades_inventario": total_stock,
            "insumos_catalogo": len(materiales),
            "insumos_bajo_minimo": len(alertas_insumos),
            "alertas_insumos": alertas_insumos,
            "ingresos_registrados": len(ingresos),
            "ordenes_activas": ordenes_activas,
            "aprobacion_calidad": resumen_calidad["aprobacion_calidad"],
            "operarios_activos": DashboardRepository.contar_operarios_activos(db),
            "valor_insumos_recibidos": valor_insumos,
            "ordenes_recientes": ProduccionService.listar_ordenes(db, limite=5),
            "actividad_reciente": TrazabilidadRepository.obtener_recientes(db, limite=8),
            **resumen_retrasos,
            "finanzas": finanzas,
        }
