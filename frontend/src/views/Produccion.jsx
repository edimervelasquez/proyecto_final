import { useState } from 'react';
import { Plus, Search, Edit2, Trash2, X } from 'lucide-react';
import '../styles/components/Produccion.css';

export default function Produccion() {
  const [busqueda, setBusqueda] = useState('');
  const [modalAbierto, setModalAbierto] = useState(false);
  const [modoEdicion, setModoEdicion] = useState(false);
  const [ordenEditarId, setOrdenEditarId] = useState(null);

  // Datos de prueba iniciales
  const [ordenes, setOrdenes] = useState([
    { id: 1, OP: 'OP-2026-01', prenda: 'Camiseta Oversize Negra', cantidad: 500, fechaEntrega: '2026-09-15', estado: 'Corte' },
    { id: 2, OP: 'OP-2026-02', prenda: 'Jean Slim Fit Azul', cantidad: 250, fechaEntrega: '2026-09-20', estado: 'Confeccion' },
    { id: 3, OP: 'OP-2026-03', prenda: 'Chaqueta Denim', cantidad: 120, fechaEntrega: '2026-09-05', estado: 'Finalizado' },
  ]);

  const [formOrden, setFormOrden] = useState({
    OP: '',
    prenda: '',
    cantidad: '',
    fechaEntrega: '',
    estado: 'Corte'
  });

  // Abrir modal para Crear
  const handleAbrirCrear = () => {
    setModoEdicion(false);
    setOrdenEditarId(null);
    setFormOrden({ OP: '', prenda: '', cantidad: '', fechaEntrega: '', estado: 'Corte' });
    setModalAbierto(true);
  };

  // Abrir modal para Editar
  const handleAbrirEditar = (item) => {
    setModoEdicion(true);
    setOrdenEditarId(item.id);
    setFormOrden({
      OP: item.OP,
      prenda: item.prenda,
      cantidad: item.cantidad,
      fechaEntrega: item.fechaEntrega,
      estado: item.estado
    });
    setModalAbierto(true);
  };

  // Función para Eliminar
  const handleEliminar = (id) => {
    if (window.confirm("¿Estás seguro de que deseas eliminar esta orden de producción?")) {
      setOrdenes(ordenes.filter(item => item.id !== id));
    }
  };

  // Guardar (Crear o Actualizar)
  const handleGuardar = (e) => {
    e.preventDefault();

    if (modoEdicion) {
      setOrdenes(ordenes.map(item => 
        item.id === ordenEditarId ? { ...formOrden, id: ordenEditarId } : item
      ));
    } else {
      setOrdenes([...ordenes, { ...formOrden, id: Date.now() }]);
    }

    setModalAbierto(false);
  };

  const ordenesFiltradas = ordenes.filter(o => 
    o.prenda.toLowerCase().includes(busqueda.toLowerCase()) || 
    o.OP.toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div className="produccion-container">
      {/* BARRA SUPERIOR DE ACCIONES */}
      <div className="produccion-header-actions">
        <div className="search-box">
          <Search size={18} color="#f59e0b" />
          <input 
            type="text" 
            placeholder="Buscar por OP o Prenda..." 
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <button className="btn-add-orden" onClick={handleAbrirCrear}>
          <Plus size={18} />
          Nueva Orden de Producción
        </button>
      </div>

      {/* TABLA DE PRODUCCIÓN */}
      <div className="table-container">
        <table className="produccion-table">
          <thead>
            <tr>
              <th>Orden (OP)</th>
              <th>Prenda / Referencia</th>
              <th>Cantidad</th>
              <th>Fecha Entrega</th>
              <th>Estado Proceso</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {ordenesFiltradas.map((item) => (
              <tr key={item.id}>
                <td><strong>{item.OP}</strong></td>
                <td>{item.prenda}</td>
                <td>{item.cantidad} Unidades</td>
                <td>{item.fechaEntrega}</td>
                <td>
                  <span className={`badge-estado ${item.estado.toLowerCase()}`}>
                    {item.estado}
                  </span>
                </td>
                <td>
                  <div className="action-buttons">
                    <button 
                      className="btn-icon edit"
                      onClick={() => handleAbrirEditar(item)}
                      title="Editar Orden"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button 
                      className="btn-icon delete"
                      onClick={() => handleEliminar(item.id)}
                      title="Eliminar Orden"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* MODAL REGISTRAR / EDITAR ORDEN DE PRODUCCIÓN */}
      {modalAbierto && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>{modoEdicion ? 'Editar Orden de Producción' : 'Registrar Orden de Producción'}</h3>
              <button className="btn-icon" onClick={() => setModalAbierto(false)}>
                <X size={20} color="#9ca3af" />
              </button>
            </div>

            <form onSubmit={handleGuardar} className="modal-form">
              <div className="form-group">
                <label>Código OP</label>
                <div className="input-wrapper">
                  <input 
                    type="text" 
                    required 
                    placeholder="Ej: OP-2026-04"
                    value={formOrden.OP}
                    onChange={(e) => setFormOrden({...formOrden, OP: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Prenda / Referencia</label>
                <div className="input-wrapper">
                  <input 
                    type="text" 
                    required 
                    placeholder="Ej: Pantalón Cargo Beige"
                    value={formOrden.prenda}
                    onChange={(e) => setFormOrden({...formOrden, prenda: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Cantidad Total</label>
                  <div className="input-wrapper">
                    <input 
                      type="number" 
                      required 
                      placeholder="0"
                      value={formOrden.cantidad}
                      onChange={(e) => setFormOrden({...formOrden, cantidad: e.target.value})}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Fecha de Entrega</label>
                  <div className="input-wrapper">
                    <input 
                      type="date" 
                      required
                      value={formOrden.fechaEntrega}
                      onChange={(e) => setFormOrden({...formOrden, fechaEntrega: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label>Estado del Proceso</label>
                <select 
                  value={formOrden.estado}
                  onChange={(e) => setFormOrden({...formOrden, estado: e.target.value})}
                >
                  <option value="Corte">En Corte</option>
                  <option value="Confeccion">En Confección</option>
                  <option value="Finalizado">Finalizado</option>
                </select>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setModalAbierto(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-add-orden">
                  {modoEdicion ? 'Actualizar Orden' : 'Crear Orden'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}