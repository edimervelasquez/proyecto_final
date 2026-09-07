import { useState } from 'react';
import { 
  Package, 
  Scissors, 
  CheckCircle, 
  Users, 
  TrendingUp, 
  DollarSign 
} from 'lucide-react';
import "../styles/Dashboard.css";
export default function Dashboard() {
  // Se remueve 'setDatos' para corregir la advertencia de ESLint
  const [datos] = useState({
    totalInsumos: 128,
    ordenesActivas: 14,
    aprobacionCalidad: 98.5,
    operariosActivos: 22,
    ingresos: 45000000,
    costos: 28000000,
  });

  const [ordenesRecientes] = useState([
    { id: 1, op: 'OP-2026-01', prenda: 'Camiseta Oversize Negra', cantidad: 500, estado: 'En Corte' },
    { id: 2, op: 'OP-2026-02', prenda: 'Jean Slim Fit Azul', cantidad: 250, estado: 'En Confección' },
    { id: 3, op: 'OP-2026-03', prenda: 'Chaqueta Denim', cantidad: 120, estado: 'Finalizado' },
  ]);

  const [alertas] = useState([
    { id: 1, item: 'Hilo 100% Poliéster Negro', estado: 'Stock Bajo', tipo: 'danger' },
    { id: 2, item: 'Auditoría Lote OP-2026-01', estado: 'Aprobado', tipo: 'success' },
  ]);

  const gananciaNeta = datos.ingresos - datos.costos;

  const formatoCOP = (valor) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(valor);
  };

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">Panel de Control Principal</h1>

      {/* TARJETAS PRINCIPALES */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="card-icon gold">
            <Package size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Total Insumos</span>
            <h2 className="card-value">{datos.totalInsumos} items</h2>
          </div>
        </div>

        <div className="metric-card">
          <div className="card-icon gold">
            <Scissors size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Órdenes Activas</span>
            <h2 className="card-value">{datos.ordenesActivas} Lotes</h2>
          </div>
        </div>

        <div className="metric-card">
          <div className="card-icon gold">
            <CheckCircle size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Aprobación Calidad</span>
            <h2 className="card-value">{datos.aprobacionCalidad}%</h2>
          </div>
        </div>

        <div className="metric-card">
          <div className="card-icon gold">
            <Users size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Operarios en Taller</span>
            <h2 className="card-value">{datos.operariosActivos} Activos</h2>
          </div>
        </div>
      </div>

      {/* SECCIÓN FINANCIERA */}
      <div className="metrics-grid" style={{ marginTop: '20px' }}>
        <div className="metric-card">
          <div className="card-icon gold">
            <DollarSign size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Ingresos Totales</span>
            <h2 className="card-value">{formatoCOP(datos.ingresos)}</h2>
          </div>
        </div>

        <div className="metric-card">
          <div className="card-icon gold">
            <DollarSign size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Costos Operativos</span>
            <h2 className="card-value">{formatoCOP(datos.costos)}</h2>
          </div>
        </div>

        <div className="metric-card">
          <div className="card-icon gold">
            <TrendingUp size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Ganancia Neta</span>
            <h2 className="card-value">{formatoCOP(gananciaNeta)}</h2>
          </div>
        </div>
      </div>

      {/* PANALES INFERIORES */}
      <div className="dashboard-sections-grid" style={{ marginTop: '25px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="dashboard-panel" style={{ background: '#111', padding: '20px', borderRadius: '8px', border: '1px solid #222' }}>
          <h3 style={{ color: '#f59e0b', marginBottom: '15px' }}>Órdenes de Producción Recientes</h3>
          <div className="recent-orders-list" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {ordenesRecientes.map((o) => (
              <div key={o.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', background: '#1a1a1a', borderRadius: '6px' }}>
                <span style={{ color: '#fff' }}><strong>{o.op}:</strong> {o.prenda} ({o.cantidad} unid)</span>
                <span style={{ color: '#f59e0b', fontWeight: 'bold' }}>{o.estado}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-panel" style={{ background: '#111', padding: '20px', borderRadius: '8px', border: '1px solid #222' }}>
          <h3 style={{ color: '#f59e0b', marginBottom: '15px' }}>Alertas del Sistema</h3>
          <div className="alerts-list" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {alertas.map((a) => (
              <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', background: '#1a1a1a', borderRadius: '6px' }}>
                <span style={{ color: '#fff' }}>{a.item}</span>
                <span style={{ color: a.tipo === 'danger' ? '#ef4444' : '#10b981', fontWeight: 'bold' }}>{a.estado}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}