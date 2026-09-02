import { useState } from 'react';
import { Plus, Search, Edit2, Trash2, X, FileText } from 'lucide-react';
import '../styles/components/FichaTecnica.css';

export default function FichaTecnica() {
  const [busqueda, setBusqueda] = useState('');
  const [modalAbierto, setModalAbierto] = useState(false);

  // Datos de prueba iniciales
  const [fichas, setFichas] = useState([
    { id: 1, referencia: 'REF-101', prenda: 'Camiseta Oversize', telaPrincipal: 'Algodón Perchado 100%', tallas: 'S, M, L, XL', fechaCreacion: '2026-08-10' },
    { id: 2, referencia: 'REF-202', prenda: 'Pantalón Cargo', telaPrincipal: 'Dril Algodón', tallas: '28, 30, 32, 34', fechaCreacion: '2026-08-15' },
    { id: 3, referencia: 'REF-303', prenda: 'Chaqueta Demin', telaPrincipal: 'Denim Rigido 14oz', tallas: 'S, M, L', fechaCreacion: '2026-08-20' },
  ]);

  const [nuevaFicha, setNuevaFicha] = useState({
    referencia: '',
    prenda: '',
    telaPrincipal: '',
    tallas: '',
    especificaciones: ''
  });

  const handleGuardar = (e) => {
    e.preventDefault();
    const fechaActual = new Date().toISOString().split('T')[0];
    setFichas([...fichas, { ...nuevaFicha, fechaCreacion: fechaActual, id: Date.now() }]);
    setModalAbierto(false);
    setNuevaFicha({ referencia: '', prenda: '', telaPrincipal: '', tallas: '', especificaciones: '' });
  };

  const fichasFiltradas = fichas.filter(f => 
    f.referencia.toLowerCase().includes(busqueda.toLowerCase()) || 
    f.prenda.toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div className="ficha-container">
      {/* BARRA SUPERIOR DE ACCIONES */}
      <div className="ficha-header-actions">
        <div className="search-box">
          <Search size={18} color="#f59e0b" />
          <input 
            type="text" 
            placeholder="Buscar por Referencia o Prenda..." 
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <button className="btn-add-ficha" onClick={() => setModalAbierto(true)}>
          <Plus size={18} />
          Nueva Ficha Técnica
        </button>
      </div>

      {/* TABLA DE FICHAS TÉCNICAS */}
      <div className="table-container">
        <table className="ficha-table">
          <thead>
            <tr>
              <th>Referencia</th>
              <th>Prenda / Diseño</th>
              <th>Tela Principal</th>
              <th>Curva de Tallas</th>
              <th>Fecha Creación</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {fichasFiltradas.map((item) => (
              <tr key={item.id}>
                <td><strong>{item.referencia}</strong></td>
                <td>{item.prenda}</td>
                <td><span className="badge-categoria">{item.telaPrincipal}</span></td>
                <td>{item.tallas}</td>
                <td>{item.fechaCreacion}</td>
                <td>
                  <div className="action-buttons">
                    <button className="btn-icon edit" title="Editar"><Edit2 size={16} /></button>
                    <button className="btn-icon delete" title="Eliminar"><Trash2 size={16} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* MODAL REGISTRAR FICHA TÉCNICA */}
      {modalAbierto && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Registrar Ficha Técnica</h3>
              <button className="btn-icon" onClick={() => setModalAbierto(false)}>
                <X size={20} color="#9ca3af" />
              </button>
            </div>

            <form onSubmit={handleGuardar} className="modal-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Código Referencia</label>
                  <div className="input-wrapper">
                    <input 
                      type="text" 
                      required 
                      placeholder="Ej: REF-404"
                      value={nuevaFicha.referencia}
                      onChange={(e) => setNuevaFicha({...nuevaFicha, referencia: e.target.value})}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Nombre de Prenda</label>
                  <div className="input-wrapper">
                    <input 
                      type="text" 
                      required 
                      placeholder="Ej: Sudadera Jogger"
                      value={nuevaFicha.prenda}
                      onChange={(e) => setNuevaFicha({...nuevaFicha, prenda: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Tela Principal</label>
                  <div className="input-wrapper">
                    <input 
                      type="text" 
                      required 
                      placeholder="Ej: Frenchn Terry"
                      value={nuevaFicha.telaPrincipal}
                      onChange={(e) => setNuevaFicha({...nuevaFicha, telaPrincipal: e.target.value})}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Curva de Tallas</label>
                  <div className="input-wrapper">
                    <input 
                      type="text" 
                      required 
                      placeholder="Ej: S, M, L"
                      value={nuevaFicha.tallas}
                      onChange={(e) => setNuevaFicha({...nuevaFicha, tallas: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label>Especificaciones y Medidas (Observaciones de Confección)</label>
                <textarea 
                  placeholder="Detalles de costura, calibre de hilo, botones o estampados..."
                  value={nuevaFicha.especificaciones}
                  onChange={(e) => setNuevaFicha({...nuevaFicha, especificaciones: e.target.value})}
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setModalAbierto(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-add-ficha">
                  Guardar Ficha
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}