import { useState } from 'react';
import axios from 'axios';
import { PackagePlus, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

function App() {
  
  const [formData, setFormData] = useState({
    id_materiaPrima: '',
    cantidad: '',
    proveedor: '',
    costo_unitario: '',
    fecha_ingreso: '' 
  });


  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

 
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMensaje(null);
    setError(null);

    try {
      
      const response = await axios.post('http://127.0.0.1:5000/api/insumos/ingreso', {
        id_materiaPrima: parseInt(formData.id_materiaPrima),
        cantidad: parseInt(formData.cantidad),
        proveedor: formData.proveedor,
        costo_unitario: parseFloat(formData.costo_unitario),
        fecha_ingreso: formData.fecha_ingreso
      });

      setMensaje(`¡Éxito! Insumo registrado. Nuevo stock: ${response.data.nuevo_stock}`);
      
      setFormData({
        id_materiaPrima: '',
        cantidad: '',
        proveedor: '',
        costo_unitario: '',
        fecha_ingreso: new Date().toISOString().split('T')[0]
      });
    } catch (err) {
      setError(err.response?.data?.error || 'No se pudo conectar con el servidor backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <PackagePlus size={28} color="#4F46E5" />
          <h2 style={styles.title}>Creaciones Yullita - Control de Insumos</h2>
        </div>
        <p style={styles.subtitle}>HU-001: Recepción y Carga de Materia Prima</p>

        {mensaje && (
          <div style={{ ...styles.alert, ...styles.successAlert }}>
            <CheckCircle2 size={20} />
            <span>{mensaje}</span>
          </div>
        )}

        {error && (
          <div style={{ ...styles.alert, ...styles.errorAlert }}>
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label style={styles.label}>ID de Materia Prima (Catálogo):</label>
            <input
              type="number"
              name="id_materiaPrima"
              value={formData.id_materiaPrima}
              onChange={handleChange}
              placeholder="Ej: 1 (Tela), 2 (Botones)"
              required
              style={styles.input}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Cantidad a Ingresar:</label>
            <input
              type="number"
              name="cantidad"
              value={formData.cantidad}
              onChange={handleChange}
              placeholder="Cantidad en metros o unidades"
              required
              style={styles.input}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Proveedor:</label>
            <input
              type="text"
              name="proveedor"
              value={formData.proveedor}
              onChange={handleChange}
              placeholder="Nombre del proveedor o distribuidor"
              style={styles.input}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Costo Unitario (COP):</label>
            <input
              type="number"
              step="0.01"
              name="costo_unitario"
              value={formData.costo_unitario}
              onChange={handleChange}
              placeholder="Valor por metro o unidad"
              style={styles.input}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Fecha de Ingreso:</label>
            <input
              type="date"
              name="fecha_ingreso"
              value={formData.fecha_ingreso}
              onChange={handleChange}
              required
              style={styles.input}
            />
          </div>

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                <span>Registrando...</span>
              </>
            ) : (
              'Registrar Entrada'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}


const styles = {
  container: { minHeight: '100vh', backgroundColor: '#f3f4f6', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px', fontFamily: 'sans-serif' },
  card: { backgroundColor: '#ffffff', padding: '30px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', width: '100%', maxWidth: '480px' },
  header: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '5px' },
  title: { fontSize: '20px', color: '#1f2937', margin: 0 },
  subtitle: { fontSize: '14px', color: '#6b7280', marginTop: 0, marginBottom: '20px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  formGroup: { display: 'flex', flexDirection: 'column', gap: '5px' },
  label: { fontSize: '14px', fontWeight: 'bold', color: '#4b5563' },
  input: { padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', outline: 'none' },
  button: { marginTop: '10px', backgroundColor: '#4f46e5', color: '#ffffff', padding: '12px', borderRadius: '6px', border: 'none', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px' },
  alert: { padding: '12px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '14px', marginBottom: '15px' },
  successAlert: { backgroundColor: '#d1fae5', color: '#065f46' },
  errorAlert: { backgroundColor: '#fee2e2', color: '#991b1b' }
};

export default App;