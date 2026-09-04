import { useState } from 'react';
import { Plus, Calculator, Trash2, X, Shirt } from 'lucide-react';
import '../styles/components/FichaTecnica.css';

export default function FichaTecnica() {
  // Lista de referencias/prendas registradas
  const [prendas, setPrendas] = useState([
    { id: 'REF-001', nombre: 'Camiseta Oversize', margenGanancia: 40 },
    { id: 'REF-002', nombre: 'Jean Slim Fit Azul', margenGanancia: 35 },
    { id: 'REF-003', nombre: 'Buso Hoodie Algodón', margenGanancia: 45 },
  ]);

  // Prenda actualmente seleccionada
  const [prendaSeleccionadaId, setPrendaSeleccionadaId] = useState('REF-001');

  // Modal de Nuevo Insumo y Modal de Nueva Prenda
  const [modalInsumoAbierto, setModalInsumoAbierto] = useState(false);
  const [modalPrendaAbierto, setModalPrendaAbierto] = useState(false);

  // Insumos asociados a cada prenda (agrupados por referencia_id)
  const [insumosPorPrenda, setInsumosPorPrenda] = useState({
    'REF-001': [
      { id: 1, insumo: 'Tela Algodón Perchado', cantidad: 1.5, unidad: 'Metros', precioUnitario: 18000 },
      { id: 2, insumo: 'Hilo Poliéster Negro', cantidad: 1, unidad: 'Carrete', precioUnitario: 3500 },
      { id: 3, insumo: 'Etiqueta Marquilla', cantidad: 2, unidad: 'Unidades', precioUnitario: 500 },
    ],
    'REF-002': [
      { id: 10, insumo: 'Tela Denim 14oz', cantidad: 1.3, unidad: 'Metros', precioUnitario: 25000 },
      { id: 11, insumo: 'Botón Metálico Jean', cantidad: 1, unidad: 'Unidades', precioUnitario: 1200 },
      { id: 12, insumo: 'Cremallera Bronce', cantidad: 1, unidad: 'Unidades', precioUnitario: 2000 },
    ],
    'REF-003': [
      { id: 20, insumo: 'Tela Perchada Mota', cantidad: 2.0, unidad: 'Metros', precioUnitario: 22000 },
      { id: 21, insumo: 'Cordón de Capota', cantidad: 1.2, unidad: 'Metros', precioUnitario: 1500 },
    ]
  });

  const [nuevoInsumo, setNuevoInsumo] = useState({
    insumo: '',
    cantidad: '',
    unidad: 'Metros',
    precioUnitario: ''
  });

  const [nuevaPrendaForm, setNuevaPrendaForm] = useState({
    referencia: '',
    nombre: '',
    margenGanancia: 40
  });

  // Datos de la prenda activa
  const prendaActiva = prendas.find(p => p.id === prendaSeleccionadaId) || prendas[0];
  const insumosActuales = insumosPorPrenda[prendaActiva.id] || [];

  // Guardar nueva referencia de ropa
  const handleCrearPrenda = (e) => {
    e.preventDefault();
    const refId = nuevaPrendaForm.referencia.toUpperCase();

    const nuevaRef = {
      id: refId,
      nombre: nuevaPrendaForm.nombre,
      margenGanancia: parseFloat(nuevaPrendaForm.margenGanancia)
    };

    setPrendas([...prendas, nuevaRef]);
    setInsumosPorPrenda({ ...insumosPorPrenda, [refId]: [] }); // Inicializa su lista vacía
    setPrendaSeleccionadaId(refId); // Selecciona automáticamente la nueva prenda
    setNuevaPrendaForm({ referencia: '', nombre: '', margenGanancia: 40 });
    setModalPrendaAbierto(false);
  };

  // Agregar insumo a la prenda activa
  const handleAgregarInsumo = (e) => {
    e.preventDefault();
    if (!nuevoInsumo.insumo || !nuevoInsumo.cantidad || !nuevoInsumo.precioUnitario) return;

    const item = {
      id: Date.now(),
      insumo: nuevoInsumo.insumo,
      cantidad: parseFloat(nuevoInsumo.cantidad),
      unidad: nuevoInsumo.unidad,
      precioUnitario: parseFloat(nuevoInsumo.precioUnitario)
    };

    setInsumosPorPrenda({
      ...insumosPorPrenda,
      [prendaActiva.id]: [...insumosActuales, item]
    });

    setNuevoInsumo({ insumo: '', cantidad: '', unidad: 'Metros', precioUnitario: '' });
    setModalInsumoAbierto(false);
  };

  const handleEliminarInsumo = (id) => {
    setInsumosPorPrenda({
      ...insumosPorPrenda,
      [prendaActiva.id]: insumosActuales.filter(item => item.id !== id)
    });
  };

  // CÁLCULOS DINÁMICOS
  const costoTotalPrenda = insumosActuales.reduce((acc, item) => acc + (item.cantidad * item.precioUnitario), 0);
  const precioSugeridoVenta = costoTotalPrenda * (1 + (prendaActiva.margenGanancia / 100));

  const formatoCOP = (valor) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(valor);
  };

  return (
    <div className="ficha-container">
      {/* BARRA SUPERIOR DE SELECCIÓN DE REFERENCIA */}
      <div className="ficha-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '15px' }}>
        <div>
          <h2 style={{ color: '#f59e0b', margin: 0 }}>Ficha Técnica & Escandallo de Costos</h2>
          
          {/* SELECTOR DE PRENDAS / REFERENCIAS */}
          <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <label style={{ color: '#9ca3af', fontWeight: 'bold' }}>Seleccionar Prenda:</label>
            <select 
              value={prendaSeleccionadaId} 
              onChange={(e) => setPrendaSeleccionadaId(e.target.value)}
              style={{ background: '#111', color: '#fff', border: '1px solid #d97706', padding: '8px 12px', borderRadius: '6px' }}
            >
              {prendas.map(p => (
                <option key={p.id} value={p.id}>
                  {p.nombre} ({p.id})
                </option>
              ))}
            </select>

            <button 
              className="btn-add-orden" 
              onClick={() => setModalPrendaAbierto(true)}
              style={{ background: '#222', border: '1px solid #f59e0b', padding: '6px 12px' }}
            >
              <Shirt size={16} /> + Nueva Referencia
            </button>
          </div>
        </div>
        
        <button className="btn-add-orden" onClick={() => setModalInsumoAbierto(true)}>
          <Plus size={18} />
          Agregar Insumo a esta Prenda
        </button>
      </div>

      {/* METRICAS DE LA PRENDA SELECCIONADA */}
      <div className="metrics-grid" style={{ marginBottom: '25px' }}>
        <div className="metric-card">
          <div className="card-icon gold">
            <Calculator size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Costo Directo ({prendaActiva.id})</span>
            <h2 className="card-value">{formatoCOP(costoTotalPrenda)}</h2>
          </div>
        </div>

        <div className="metric-card">
          <div className="card-icon gold">
            <Calculator size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Margen Ganancia</span>
            <h2 className="card-value">{prendaActiva.margenGanancia}%</h2>
          </div>
        </div>

        <div className="metric-card">
          <div className="card-icon gold">
            <Calculator size={24} />
          </div>
          <div className="card-info">
            <span className="card-title">Precio Venta Sugerido</span>
            <h2 className="card-value" style={{ color: '#10b981' }}>{formatoCOP(precioSugeridoVenta)}</h2>
          </div>
        </div>
      </div>

      {/* TABLA DE INSUMOS DE LA REFERENCIA SELECCIONADA */}
      <div className="table-container">
        <table className="produccion-table">
          <thead>
            <tr>
              <th>Insumo / Material</th>
              <th>Consumo Requerido</th>
              <th>Costo Unitario</th>
              <th>Costo Total en Prenda</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {insumosActuales.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', color: '#9ca3af', padding: '20px' }}>
                  No hay insumos registrados para {prendaActiva.nombre}.
                </td>
              </tr>
            ) : (
              insumosActuales.map((item) => (
                <tr key={item.id}>
                  <td><strong>{item.insumo}</strong></td>
                  <td>{item.cantidad} {item.unidad}</td>
                  <td>{formatoCOP(item.precioUnitario)}</td>
                  <td><strong>{formatoCOP(item.cantidad * item.precioUnitario)}</strong></td>
                  <td>
                    <button className="btn-icon delete" onClick={() => handleEliminarInsumo(item.id)}>
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* MODAL 1: REGISTRAR NUEVA REFERENCIA DE PRENDA */}
      {modalPrendaAbierto && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Crear Nueva Referencia de Ropa</h3>
              <button className="btn-icon" onClick={() => setModalPrendaAbierto(false)}>
                <X size={20} color="#9ca3af" />
              </button>
            </div>
            <form onSubmit={handleCrearPrenda} className="modal-form">
              <div className="form-group">
                <label>Código Referencia</label>
                <input 
                  type="text" 
                  required 
                  placeholder="Ej: REF-004 o JEAN-01"
                  value={nuevaPrendaForm.referencia}
                  onChange={(e) => setNuevaPrendaForm({...nuevaPrendaForm, referencia: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Nombre de la Prenda</label>
                <input 
                  type="text" 
                  required 
                  placeholder="Ej: Jean Cargo Negro, Buso Oversize"
                  value={nuevaPrendaForm.nombre}
                  onChange={(e) => setNuevaPrendaForm({...nuevaPrendaForm, nombre: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Margen de Ganancia (%)</label>
                <input 
                  type="number" 
                  required 
                  placeholder="Ej: 40"
                  value={nuevaPrendaForm.margenGanancia}
                  onChange={(e) => setNuevaPrendaForm({...nuevaPrendaForm, margenGanancia: e.target.value})}
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setModalPrendaAbierto(false)}>Cancelar</button>
                <button type="submit" className="btn-add-orden">Crear Referencia</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: AGREGAR INSUMO A LA PRENDA ACTIVA */}
      {modalInsumoAbierto && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Agregar Insumo a {prendaActiva.nombre}</h3>
              <button className="btn-icon" onClick={() => setModalInsumoAbierto(false)}>
                <X size={20} color="#9ca3af" />
              </button>
            </div>
            <form onSubmit={handleAgregarInsumo} className="modal-form">
              <div className="form-group">
                <label>Nombre del Insumo</label>
                <input 
                  type="text" 
                  required 
                  placeholder="Ej: Cremallera, Tela Denim, Botón"
                  value={nuevoInsumo.insumo}
                  onChange={(e) => setNuevoInsumo({...nuevoInsumo, insumo: e.target.value})}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Cantidad Consumida</label>
                  <input 
                    type="number" 
                    step="0.01" 
                    required 
                    placeholder="Ej: 1.5"
                    value={nuevoInsumo.cantidad}
                    onChange={(e) => setNuevoInsumo({...nuevoInsumo, cantidad: e.target.value})}
                  />
                </div>

                <div className="form-group">
                  <label>Unidad</label>
                  <select 
                    value={nuevoInsumo.unidad}
                    onChange={(e) => setNuevoInsumo({...nuevoInsumo, unidad: e.target.value})}
                  >
                    <option value="Metros">Metros</option>
                    <option value="Unidades">Unidades</option>
                    <option value="Carrete">Carrete</option>
                    <option value="Kilos">Kilos</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Precio Unitario Insumo (COP)</label>
                <input 
                  type="number" 
                  required 
                  placeholder="Ej: 15000"
                  value={nuevoInsumo.precioUnitario}
                  onChange={(e) => setNuevoInsumo({...nuevoInsumo, precioUnitario: e.target.value})}
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setModalInsumoAbierto(false)}>Cancelar</button>
                <button type="submit" className="btn-add-orden">Guardar en Ficha</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}