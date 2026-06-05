import { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart3, CheckCircle, AlertTriangle, Activity, Loader2, DollarSign} from 'lucide-react';

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    total_recibido: 0,
    total_optimo: 0,
    total_defectuoso: 0,
    eficiencia: 100
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Consumimos el endpoint de rendimiento que creamos en el backend
    axios.get('http://127.0.0.1:5000/api/dashboard/rendimiento')
      .then((response) => {
        setMetrics(response.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Detalle del error:", err); // <-- Aquí usamos 'err'
        setError('No se pudieron cargar las métricas en tiempo real.');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={styles.loadingBox}>
        <Loader2 className="animate-spin" size={32} color="#1e293b" />
        <p>Cargando balance de producción...</p>
      </div>
    );
  }

  return (
    <div>
      <div style={styles.header}>
        <BarChart3 size={28} color="#1e293b" />
        <h2 style={styles.title}>Dashboard de Rendimiento - Creaciones Yullita</h2>
      </div>
      <p style={styles.subtitle}>Análisis analítico de eficiencia y control de mermas en el taller</p>

      {error && <div style={styles.errorAlert}>{error}</div>}

      {/* TARJETAS DE INDICADORES (KPIs) */}
      <div style={styles.grid}>
        
        <div style={{ ...styles.card, borderLeft: '5px solid #3b82f6' }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Total Confeccionado</span>
            <Activity size={20} color="#3b82f6" />
          </div>
          <p style={styles.cardValue}>{metrics.total_recibido} <span style={styles.unit}>Uds</span></p>
        </div>

        <div style={{ ...styles.card, borderLeft: '5px solid #10b981' }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Prendas Óptimas</span>
            <CheckCircle size={20} color="#10b981" />
          </div>
          <p style={styles.cardValue}>{metrics.total_optimo} <span style={styles.unit}>Uds</span></p>
        </div>

        <div style={{ ...styles.card, borderLeft: '5px solid #ef4444' }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Prendas Defectuosas</span>
            <AlertTriangle size={20} color="#ef4444" />
          </div>
          <p style={styles.cardValue}>{metrics.total_defectuoso} <span style={styles.unit}>Uds</span></p>
        </div>

        <div style={{ ...styles.card, borderLeft: '5px solid #8b5cf6' }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Eficiencia Operativa</span>
            <BarChart3 size={20} color="#8b5cf6" />
          </div>
          <p style={styles.cardValue}>{metrics.eficiencia}<span style={styles.unit}>%</span></p>
        </div>

        {/* NUEVA TARJETA: PRECIO REFERENCIAL */}
        <div style={{ ...styles.card, borderLeft: '5px solid #f59e0b' }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Precio Promedio Prenda</span>
            <DollarSign size={20} color="#f59e0b" />
          </div>
          <p style={styles.cardValue}>${metrics.precio_unitario?.toLocaleString('es-CO')}</p>
        </div>

        {/* NUEVA TARJETA: TOTAL PRODUCIDO EN VALOR MONETARIO */}
        <div style={{ ...styles.card, borderLeft: '5px solid #10b981' }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Valor Total Producido</span>
            <DollarSign size={20} color="#10b981" />
          </div>
          <p style={styles.cardValue}>${metrics.total_monetario?.toLocaleString('es-CO')} <span style={styles.unit}>COP</span></p>
        </div>

      </div>

      {/* SECCIÓN INFORMATIVA DE AUDITORÍA */}
      <div style={styles.infoSection}>
        <h3>Estado General del Taller</h3>
        <p>
          El porcentaje de eficiencia actual del <strong>{metrics.eficiencia}%</strong> refleja la relación entre los insumos descontados contra las prendas que pasaron con éxito los estándares de calidad establecidos para la distribución de ropa infantil.
        </p>
      </div>
    </div>
  );
}

const styles = {
  header: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '5px' },
  title: { fontSize: '24px', color: '#1f2937', margin: 0 },
  subtitle: { fontSize: '14px', color: '#6b7280', marginTop: 0, marginBottom: '30px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '30px' },
  card: { backgroundColor: '#ffffff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', display: 'flex', flexDirection: 'column', gap: '10px' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { fontSize: '14px', color: '#4b5563', fontWeight: '600' },
  cardValue: { fontSize: '28px', fontWeight: 'bold', color: '#111827', margin: 0 },
  unit: { fontSize: '16px', fontWeight: 'normal', color: '#6b7280', marginLeft: '5px' },
  infoSection: { backgroundColor: '#ffffff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', color: '#374151', lineHeight: '1.6' },
  loadingBox: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '10px', height: '200px', color: '#4b5563' },
  errorAlert: { padding: '12px', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '6px', marginBottom: '20px', fontSize: '14px' }
};