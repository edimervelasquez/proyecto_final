import { useEffect, useState } from 'react';
import {
  Package,
  Scissors,
  CheckCircle,
  Users,
  ClipboardList,
  DollarSign,
  TrendingUp,
} from 'lucide-react';
import TrazabilidadTable from '../../components/TrazabilidadTable';
import { dashboardService } from '../../services/dashboardService';
import '../../styles/Dashboard.css';

const formatoCOP = (valor) => new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
}).format(valor || 0);

const tipoLegible = (tipo) => ({
  ingreso_insumo: 'Ingreso de insumo',
  ficha_tecnica: 'Ficha técnica',
  orden_produccion: 'Orden de producción',
  control_calidad: 'Control de calidad',
}[tipo] || tipo);

export default function Dashboard() {
  const [resumen, setResumen] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  const actualizar = async () => {
    setCargando(true);
    setError('');
    try {
      const data = await dashboardService.obtenerResumen();
      setResumen(data);
    } catch (err) {
      setError(err.message || 'No se pudo cargar el dashboard.');
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    let activo = true;
    dashboardService.obtenerResumen()
      .then((data) => {
        if (activo) setResumen(data);
      })
      .catch((err) => {
        if (activo) setError(err.message || 'No se pudo cargar el dashboard.');
      })
      .finally(() => {
        if (activo) setCargando(false);
      });
    return () => {
      activo = false;
    };
  }, []);

  const ordenes = (resumen?.ordenes_recientes || []).map((orden) => ({
    ...orden,
    referencia: `OP-${orden.id_orden}`,
    detalle: `${orden.sku_prenda} · ${orden.cantidad} unidades · ${orden.area}`,
  }));

  const actividad = (resumen?.actividad_reciente || []).map((registro) => ({
    ...registro,
    id: `${registro.tipo_registro}-${registro.referencia}`,
    referencia: `${tipoLegible(registro.tipo_registro)} #${registro.referencia}`,
    detalle: registro.nombre_registro,
  }));

  const retrasos = (resumen?.retrasos_recientes || []).map((registro) => ({
    ...registro,
    id: registro.id_retraso,
    referencia: `OP-${registro.id_orden} · ${registro.area}`,
    detalle: `${registro.motivo}${registro.detalle ? ` — ${registro.detalle}` : ''}`,
    fecha_registro: registro.fecha_inicio,
    proceso: registro.area,
    estado: registro.abierto
      ? `En curso · ${registro.minutos_detenida} min`
      : `${registro.minutos_detenida} min`,
  }));

  const gruposMetricas = resumen ? [
    {
      titulo: 'Inventario y producción',
      metricas: [
        { titulo: 'Referencias de insumos', valor: resumen.insumos_catalogo, icono: <Package size={22} /> },
        { titulo: 'Insumos bajo mínimo', valor: resumen.insumos_bajo_minimo, icono: <Package size={22} /> },
        { titulo: 'Unidades en inventario', valor: resumen.unidades_inventario, icono: <ClipboardList size={22} /> },
        { titulo: 'Órdenes activas', valor: resumen.ordenes_activas, icono: <Scissors size={22} /> },
      ],
    },
    {
      titulo: 'Calidad y operación',
      metricas: [
        { titulo: 'Aprobación de calidad', valor: `${resumen.aprobacion_calidad}%`, icono: <CheckCircle size={22} /> },
        { titulo: 'Operarios activos', valor: resumen.operarios_activos, icono: <Users size={22} /> },
        { titulo: 'Ingresos de insumos', valor: resumen.ingresos_registrados, icono: <Package size={22} /> },
        { titulo: 'Valor registrado de insumos', valor: formatoCOP(resumen.valor_insumos_recibidos), icono: <DollarSign size={22} /> },
        { titulo: 'Retrasos abiertos', valor: resumen.retrasos_abiertos, icono: <ClipboardList size={22} /> },
        {
          titulo: 'Tiempo perdido por retrasos',
          valor: `${Math.floor(resumen.tiempo_perdido_minutos / 60)} h ${resumen.tiempo_perdido_minutos % 60} min`,
          icono: <Scissors size={22} />,
        },
      ],
    },
    {
      titulo: 'Resumen financiero',
      metricas: [
        { titulo: 'Ventas totales', valor: formatoCOP(resumen.finanzas?.ventas_totales), icono: <DollarSign size={22} /> },
        { titulo: 'Ventas mayoristas', valor: formatoCOP(resumen.finanzas?.ventas_mayoristas), icono: <DollarSign size={22} /> },
        { titulo: 'Ventas al detal', valor: formatoCOP(resumen.finanzas?.ventas_detal), icono: <DollarSign size={22} /> },
        { titulo: 'Costo de prendas vendidas', valor: formatoCOP(resumen.finanzas?.costo_productos_vendidos), icono: <Package size={22} /> },
        { titulo: 'Margen bruto', valor: formatoCOP(resumen.finanzas?.margen_bruto), icono: <TrendingUp size={22} /> },
        { titulo: 'Pérdida estimada por calidad', valor: formatoCOP(resumen.finanzas?.perdida_estimada_calidad), icono: <Scissors size={22} /> },
        { titulo: 'Margen después de rechazos', valor: formatoCOP(resumen.finanzas?.margen_despues_rechazos), icono: <TrendingUp size={22} /> },
      ],
    },
  ] : [];

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">SIES Yullita</p>
          <h1 className="dashboard-title">Panel de control</h1>
          <p className="dashboard-subtitle">Resumen de inventario, producción y resultados del taller.</p>
        </div>
        <button
          type="button"
          className="dashboard-refresh"
          onClick={actualizar}
          disabled={cargando}
        >
          {cargando ? 'Actualizando...' : 'Actualizar información'}
        </button>
      </header>
      {cargando && <p role="status">Cargando información real del sistema...</p>}
      {error && <p className="trazabilidad-error" role="alert">{error}</p>}
      {!cargando && !error && resumen && (
        <>
          {gruposMetricas.map((grupo, indice) => (
            <section
              className="dashboard-metric-section"
              key={grupo.titulo}
              aria-labelledby={`dashboard-metrics-${indice}`}
            >
              <h2 id={`dashboard-metrics-${indice}`} className="dashboard-section-title">
                {grupo.titulo}
              </h2>
              <div className="metrics-grid">
                {grupo.metricas.map((metrica) => (
                  <article className="metric-card" key={metrica.titulo}>
                    <div className="card-icon gold">{metrica.icono}</div>
                    <div className="card-info">
                      <span className="card-title">{metrica.titulo}</span>
                      <h3 className="card-value">{metrica.valor}</h3>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          ))}

          <section className="dashboard-stock-alerts" aria-labelledby="stock-alerts-title">
            <h2 id="stock-alerts-title">Alertas de materia prima</h2>
            {(resumen.alertas_insumos || []).length === 0
              ? <p>No hay insumos en el mínimo o por debajo de este.</p>
              : (
                <ul>
                  {resumen.alertas_insumos.map((material) => (
                    <li key={material.id_materiaPrima}>
                      <strong>{material.nombre_material}</strong>
                      <span>Disponible: {material.stock} · Mínimo: {material.stock_minimo}</span>
                    </li>
                  ))}
                </ul>
              )}
          </section>

          <TrazabilidadTable
            titulo="Órdenes de producción recientes"
            registros={ordenes}
            cargando={false}
            error=""
            vacio="Todavía no hay órdenes de producción."
          />
          <p className="dashboard-finance-note">
            {resumen.finanzas?.nota}
          </p>

          <TrazabilidadTable
            titulo="Retrasos recientes"
            registros={retrasos}
            cargando={false}
            error=""
            vacio="Todavía no se han registrado retrasos."
          />

          <TrazabilidadTable
            titulo="Actividad reciente"
            registros={actividad}
            cargando={false}
            error=""
            vacio="Todavía no hay actividad registrada."
          />
        </>
      )}
    </div>
  );
}
