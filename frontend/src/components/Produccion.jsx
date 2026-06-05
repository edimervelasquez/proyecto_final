import { useState } from 'react';
import axios from 'axios';
import { ClipboardCopy, Loader2, CheckCircle2, AlertTriangle, Calendar } from 'lucide-react';

export default function Produccion() {
  const [formData, setFormData] = useState({
    id_area: '1', // Por defecto toma el área 1 que acabamos de crear en la base de datos
    sku_prenda: '',
    cantidad_a_producir: '',
    fecha_entrega: ''
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
      const response = await axios.post('http://127.0.0.1:5000/api/produccion/orden', {
        id_area: parseInt(formData.id_area),
        sku_prenda: formData.sku_prenda,
        cantidad_a_producir: parseInt(formData.cantidad_a_producir),
        fecha_entrega: formData.fecha_entrega
      });

      setMensaje(response.data.mensaje);
      // Limpiamos el formulario excepto el área
      setFormData({ id_area: '1', sku_prenda: '', cantidad_a_producir: '', fecha_entrega: '' });
    } catch (err) {
      setError(err.response?.data?.error || 'Error al conectar con el servidor backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <ClipboardCopy size={28} color="#0EA5E9" />
        <h2 style={styles.title}>Creaciones Yullita - Orden de Producción</h2>
      </div>
      <p style={styles.subtitle}>HU-003: Lanzamiento de Lote y Descuento Automático de Inventario</p>

      {mensaje && (
        <div style={{ ...styles.alert, ...styles.successAlert }}>
          <CheckCircle2 size={20} />
          <div>
            <strong>{mensaje}</strong>
            <p style={{ margin: '5px 0 0 0', fontSize: '13px' }}>El inventario de materia prima ha sido actualizado.</p>
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
          <label style={styles.label}>Área de Trabajo / Taller:</label>
          <select name="id_area" value={formData.id_area} onChange={handleChange} style={styles.input}>
            <option value="1">Taller de Confección Principal (ID: 1)</option>
          </select>
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>SKU de la Prenda (Ficha Técnica):</label>
          <input type="text" name="sku_prenda" value={formData.sku_prenda} onChange={handleChange} placeholder="Ej: VEST-INF-1" required style={styles.input} />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Cantidad de Prendas a Fabricar:</label>
          <input type="number" name="cantidad_a_producir" value={formData.cantidad_a_producir} onChange={handleChange} placeholder="Ej: 50" required style={styles.input} />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Fecha Pactada de Entrega:</label>
          <input type="date" name="fecha_entrega" value={formData.fecha_entrega} onChange={handleChange} required style={styles.input} />
        </div>

        <button type="submit" disabled={loading} style={styles.button}>
          {loading ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              <span>Verificando Stock y Creando Orden...</span>
            </>
          ) : (
            <>
              <Calendar size={18} />
              <span>Lanzar Orden a Producción</span>
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
  button: { marginTop: '10px', backgroundColor: '#0ea5e9', color: '#ffffff', padding: '12px', borderRadius: '6px', border: 'none', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px' },
  alert: { padding: '15px', borderRadius: '6px', display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '14px', marginBottom: '15px' },
  successAlert: { backgroundColor: '#d1fae5', color: '#065f46' },
  errorAlert: { backgroundColor: '#fee2e2', color: '#991b1b' }
};