import { useState } from 'react';
import { Plus, Search, Edit2, Trash2, X } from 'lucide-react';
import '../styles/components/IngresoInsumos.css';

export default function IngresoInsumos() {
  const [busqueda, setBusqueda] = useState('');
  const [modalAbierto, setModalAbierto] = useState(false);

  // Datos iniciales de prueba
  const [insumos, setInsumos] = useState([
    { id: 1, codigo: 'INS-001', nombre: 'Hilo Algodón 40/2 Negro', categoria: 'Hilos', stock: 45, unidad: 'Conos', min: 10 },
    { id: 2, codigo: 'INS-002', nombre: 'Cremallera Invisible 20cm', categoria: 'Cierres', stock: 5, unidad: 'Unidades', min: 15 },
    { id: 3, codigo: 'INS-003', nombre: 'Tela Denim 12oz Azul', categoria: 'Telas', stock: 120, unidad: 'Metros', min: 20 },
  ]);

  const [nuevoInsumo, setNuevoInsumo] = useState({
    codigo: '',
    nombre: '',
    categoria: 'Hilos',
    stock: '',
    unidad: 'Unidades',
    min: ''
  });

  const handleGuardar = (e) => {
    e.preventDefault();
    setInsumos([...insumos, { ...nuevoInsumo, id: Date.now() }]);
    setModalAbierto(false);
    setNuevoInsumo({ codigo: '', nombre: '', categoria: 'Hilos', stock: '', unidad: 'Unidades', min: '' });
  };

  const insumosFiltrados = insumos.filter(i => 
    i.nombre.toLowerCase().includes(busqueda.toLowerCase()) || 
    i.codigo.toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div className="insumos-container">
      {/* BARRA SUPERIOR DE ACCIONES */}
      <div className="insumos-header-actions">
        <div className="search-box">
          <Search size={18} color="#f59e0b" />
          <input 
            type="text" 
            placeholder="Buscar por código o nombre..." 
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <button className="btn-add-insumo" onClick={() => setModalAbierto(true)}>
          <Plus size={18} />
          Nuevo Insumo
        </button>
      </div>

      {/* TABLA DE INSUMOS */}
      <div className="table-container">
        <table className="insumos-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre del Insumo</th>
              <th>Categoría</th>
              <th>Stock</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {insumosFiltrados.map((item) => {
              const esCritico = Number(item.stock) <= Number(item.min);
              return (
                <tr key={item.id}>
                  <td><strong>{item.codigo}</strong></td>
                  <td>{item.nombre}</td>
                  <td>{item.categoria}</td>
                  <td>{item.stock} {item.unidad}</td>
                  <td>
                    <span className={`badge-stock ${esCritico ? 'critico' : 'normal'}`}>
                      {esCritico ? 'Stock Crítico' : 'Disponible'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button className="btn-icon edit"><Edit2 size={16} /></button>
                      <button className="btn-icon delete"><Trash2 size={16} /></button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* MODAL REGISTRAR INSUMO */}
      {modalAbierto && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Registrar Nuevo Insumo</h3>
              <button className="btn-icon" onClick={() => setModalAbierto(false)}>
                <X size={20} color="#9ca3af" />
              </button>
            </div>

            <form onSubmit={handleGuardar} className="modal-form">
              <div className="form-group">
                <label>Código</label>
                <div className="input-wrapper">
                  <input 
                    type="text" 
                    required 
                    placeholder="Ej: INS-004"
                    value={nuevoInsumo.codigo}
                    onChange={(e) => setNuevoInsumo({...nuevoInsumo, codigo: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Nombre del Insumo</label>
                <div className="input-wrapper">
                  <input 
                    type="text" 
                    required 
                    placeholder="Ej: Botón Metálico 15mm"
                    value={nuevoInsumo.nombre}
                    onChange={(e) => setNuevoInsumo({...nuevoInsumo, nombre: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Categoría</label>
                  <div className="input-wrapper">
                    <input 
                      type="text" 
                      placeholder="Hilos, Botones..." 
                      value={nuevoInsumo.categoria}
                      onChange={(e) => setNuevoInsumo({...nuevoInsumo, categoria: e.target.value})}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Unidad Medida</label>
                  <div className="input-wrapper">
                    <input 
                      type="text" 
                      placeholder="Metros, Conos..." 
                      value={nuevoInsumo.unidad}
                      onChange={(e) => setNuevoInsumo({...nuevoInsumo, unidad: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Cantidad Stock</label>
                  <div className="input-wrapper">
                    <input 
                      type="number" 
                      required 
                      placeholder="0"
                      value={nuevoInsumo.stock}
                      onChange={(e) => setNuevoInsumo({...nuevoInsumo, stock: e.target.value})}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Mínimo Mantenimiento</label>
                  <div className="input-wrapper">
                    <input 
                      type="number" 
                      required 
                      placeholder="0"
                      value={nuevoInsumo.min}
                      onChange={(e) => setNuevoInsumo({...nuevoInsumo, min: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setModalAbierto(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-add-insumo">
                  Guardar Insumo
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}