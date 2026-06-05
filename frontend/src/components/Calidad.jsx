import { useState } from 'react';
import axios from 'axios';
import { CheckCircle, Loader2, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function Calidad() {
  const [formData, setFormData] = useState({
    id_produccion: '',
    cantidad_optima: '',
    cantidad_defectuosa: ''
  });

  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMensaje(null);
    setError(null);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/produccion/calidad', {
        id_produccion: parseInt(formData.id_produccion),
        cantidad_optima: parseInt(formData.cantidad_optima),
        cantidad_defectuosa: parseInt(formData.cantidad_defectuosa)
      });

      setMensaje(response.data.mensaje);
      setFormData({ id_produccion: '', cantidad_optima: '', cantidad_defectuosa: '' });
    } catch (err) {
      setError(err.response?.data?.error || 'Error al procesar el control de calidad.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <ShieldCheck size={28} color="#10B981" />
        <h2 style={styles.title}>Creaciones Yullita - Control de Calidad</h2>
      </div>
      <p style={styles.subtitle}>HU-004 / HU-005: Auditoría de Lotes y Cierre de Producción</p>

      {mensaje && (
        <div style={{ ...styles.alert, ...styles.successAlert }}>
          <CheckCircle2 size={20} />
          <div>
            <strong>{mensaje}</strong>
            <p style={{ margin: '5px 0 0 0', fontSize: '13px' }}>El lote ha sido cerrado y las prendas aprobadas están listas.</p>
          </div>
        </div>
      )}

      {error && (
        <div style={{ ...styles.alert, ...styles.errorAlert }}>
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.formGroup}>
          <label style={styles.label}>Número / ID de la Orden de Producción:</label>
          <input type="number" name="id_produccion" value={formData.id_produccion} onChange={handleChange} placeholder="Ej: 1" required style={styles.input} />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Prendas Óptimas (Aprobadas):</label>
          <input type="number" name="cantidad_optima" value={formData.cantidad_optima} onChange={handleChange} placeholder="Ej: 18" required style={styles.input} />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Prendas Defectuosas (Dañadas):</label>
          <input type="number" name="cantidad_defectuosa" value={formData.cantidad_defectuosa} onChange={handleChange} placeholder="Ej: 2" required style={styles.input} />
        </div>

        <button type="submit" disabled={loading} style={styles.button}>
          {loading ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              <span>Validando Cantidades...</span>
            </>
          ) : (
            <>
              <CheckCircle size={18} />
              <span>Cerrar Lote y Auditar</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}

const styles = {
  card: { backgroundColor: '#ffffff', padding: '30px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', width: '100%', maxWidth: '520px', margin: '20px auto' },
  header: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '5px' },
  title: { fontSize: '20px', color: '#1f2937', margin: 0 },
  subtitle: { fontSize: '14px', color: '#6b7280', marginTop: 0, marginBottom: '20px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  formGroup: { display: 'flex', flexDirection: 'column', gap: '5px' },
  label: { fontSize: '14px', fontWeight: 'bold', color: '#4b5563' },
  input: { padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', outline: 'none' },
  button: { marginTop: '10px', backgroundColor: '#10b981', color: '#ffffff', padding: '12px', borderRadius: '6px', border: 'none', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px' },
  alert: { padding: '15px', borderRadius: '6px', display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '14px', marginBottom: '15px' },
  successAlert: { backgroundColor: '#d1fae5', color: '#065f46' },
  errorAlert: { backgroundColor: '#fee2e2', color: '#991b1b' }
};