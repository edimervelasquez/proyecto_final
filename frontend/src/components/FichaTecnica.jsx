import { useState } from 'react';
import axios from 'axios';
import { Plus, Trash2, Calculator,  CheckCircle, AlertTriangle } from 'lucide-react';

export default function FichaTecnica() {
  const [skuPrenda, setSkuPrenda] = useState('');
  const [manoObra, setManoObra] = useState('');
  
  // Lista dinámica de insumos asignados a la prenda
  const [insumosPrenda, setInsumosPrenda] = useState([
    { id_materiaPrima: '', cantidad_estimada: '' }
  ]);

  const [resultadoCosteo, setResultadoCosteo] = useState(null);
  const [error, setError] = useState(null);

  // Agregar una nueva fila de insumo en la interfaz
  const agregarInsumoFila = () => {
    setInsumosPrenda([...insumosPrenda, { id_materiaPrima: '', cantidad_estimada: '' }]);
  };

  // Eliminar una fila de insumo
  const eliminarInsumoFila = (index) => {
    const nuevosInsumos = insumosPrenda.filter((_, i) => i !== index);
    setInsumosPrenda(nuevosInsumos);
  };

  // Manejar el cambio de datos dentro de las filas de insumos
  const handleInsumoChange = (index, e) => {
    const { name, value } = e.target;
    const nuevosInsumos = [...insumosPrenda];
    nuevosInsumos[index][name] = value;
    setInsumosPrenda(nuevosInsumos);
  };

  const procesarFicha = async (e) => {
    e.preventDefault();
    setError(null);
    setResultadoCosteo(null);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/ficha-tecnica', {
        sku_prenda: skuPrenda,
        costo_mano_obra: parseFloat(manoObra || 0),
        insumos: insumosPrenda.map(item => ({
          id_materiaPrima: parseInt(item.id_materiaPrima),
          cantidad_estimada: parseFloat(item.cantidad_estimada)
        }))
      });
      setResultadoCosteo(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Error al procesar los costos de la ficha técnica.');
    }
  };

  return (
    <div style={styles.card}>
      <h2>HU-002: Ficha Técnica y Costeo de Producción</h2>
      <p style={{ color: '#6b7280', fontSize: '14px' }}>Define los insumos y mano de obra requeridos para calcular costos unitarios exactos.</p>
      
      {error && <div style={styles.errorAlert}><AlertTriangle size={18}/> {error}</div>}
      {resultadoCosteo && (
        <div style={styles.successAlert}>
          <CheckCircle size={18}/> 
          <div>
            <strong>{resultadoCosteo.mensaje}</strong>
            <div style={{ marginTop: '5px', fontSize: '13px' }}>
              • Costo Materiales: ${resultadoCosteo.costo_materiales.toFixed(2)} COP <br/>
              • Costo Mano de Obra: ${resultadoCosteo.costo_mano_obra.toFixed(2)} COP <br/>
              • <strong>Costo Total Fabricación: ${resultadoCosteo.costo_total_fabricacion.toFixed(2)} COP</strong>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={procesarFicha} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'flex', gap: '15px' }}>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <label style={styles.label}>Código/SKU de Prenda:</label>
            <input type="text" value={skuPrenda} onChange={(e) => setSkuPrenda(e.target.value)} placeholder="Ej: VEST-INF-01" required style={styles.input}/>
          </div>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <label style={styles.label}>Costo Mano de Obra (Prenda):</label>
            <input type="number" value={manoObra} onChange={(e) => setManoObra(e.target.value)} placeholder="Ej: 3500" required style={styles.input}/>
          </div>
        </div>

        <div>
          <h4 style={{ margin: '10px 0', color: '#374151' }}>Insumos y Consumo por Prenda</h4>
          {insumosPrenda.map((insumo, index) => (
            <div key={index} style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '10px' }}>
              <input type="number" name="id_materiaPrima" value={insumo.id_materiaPrima} onChange={(e) => handleInsumoChange(index, e)} placeholder="ID Insumo (Ej: 1)" required style={{ ...styles.input, flex: 2 }}/>
              <input type="number" step="0.01" name="cantidad_estimada" value={insumo.cantidad_estimada} onChange={(e) => handleInsumoChange(index, e)} placeholder="Cant. Necesaria (Ej: 0.5)" required style={{ ...styles.input, flex: 2 }}/>
              {insumosPrenda.length > 1 && (
                <button type="button" onClick={() => eliminarInsumoFila(index)} style={styles.btnDelete}><Trash2 size={16}/></button>
              )}
            </div>
          ))}
          <button type="button" onClick={agregarInsumoFila} style={styles.btnAdd}><Plus size={16}/> Añadir Insumo</button>
        </div>

        <button type="submit" style={styles.btnSubmit}><Calculator size={18}/> Calcular Costos y Guardar Ficha</button>
      </form>
    </div>
  );
}

const styles = {
  card: { backgroundColor: '#fff', padding: '35px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', width: '100%', maxWidth: '600px', margin: '0 auto' },
  label: { fontSize: '14px', fontWeight: 'bold', color: '#4b5563' },
  input: { padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', outline: 'none' },
  btnAdd: { padding: '8px 12px', backgroundColor: '#e0e7ff', color: '#4338ca', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', display: 'inline-flex', alignItems: 'center', gap: '5px', fontWeight: 'bold', marginTop: '5px' },
  btnDelete: { backgroundColor: '#fee2e2', color: '#b91c1c', border: 'none', padding: '10px', borderRadius: '6px', cursor: 'pointer' },
  btnSubmit: { backgroundColor: '#4f46e5', color: '#fff', padding: '14px', border: 'none', borderRadius: '6px', fontSize: '15px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', marginTop: '10px' },
  errorAlert: { backgroundColor: '#fee2e2', color: '#991b1b', padding: '12px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px', fontSize: '14px' },
  successAlert: { backgroundColor: '#d1fae5', color: '#065f46', padding: '15px', borderRadius: '6px', display: 'flex', gap: '10px', marginBottom: '15px', fontSize: '14px', lineHeight: '1.4' }
};