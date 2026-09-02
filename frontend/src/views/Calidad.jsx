import { useState } from 'react';
import { Plus, Search, Edit2, Trash2, X } from 'lucide-react';
import '../styles/components/Calidad.css';

export default function Calidad() {
  const [busqueda, setBusqueda] = useState('');
  const [modalAbierto, setModalAbierto] = useState(false);

  // Datos de prueba iniciales
  const [reportes, setReportes] = useState([
    { id: 1, OP: 'OP-2026-01', inspector: 'Carlos Ruiz', auditadas: 100, defectuosas: 2, estado: 'Aprobado' },
    { id: 2, OP: 'OP-2026-02', inspector: 'Ana Gomez', auditadas: 50, defectuosas: 8, estado: 'Rechazado' },
    { id: 3, OP: 'OP-2026-03', inspector: 'Carlos Ruiz', auditadas: 30, defectuosas: 0, estado: 'Pendiente' },
  ]);

  const [nuevoReporte, setNuevoReporte] = useState({
    OP: '',
    inspector: '',
    auditadas: '',
    defectuosas: '',
    estado: 'Aprobado'
  });

  const handleGuardar = (e) => {
    e.preventDefault();
    setReportes([...reportes, { ...nuevoReporte, id: Date.now() }]);
    setModalAbierto(false);
    setNuevoReporte({ OP: '', inspector: '', auditadas: '', defectuosas: '', estado: 'Aprobado' });
  };

  const reportesFiltrados = reportes.filter(r => 
    r.OP.toLowerCase().includes(busqueda.toLowerCase()) || 
    r.inspector.toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div className="calidad-container">
      {/* BARRA SUPERIOR DE ACCIONES */}
      <div className="calidad-header-actions">
        <div className="search-box">
          <Search size={18} color="#f59e0b" />
          <input 
            type="text" 
            placeholder="Buscar por OP o Auditor..." 
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <button className="btn-add-auditoria" onClick={() => setModalAbierto(true)}>
          <Plus size={18} />
          Nueva Auditoría
        </button>
      </div>

      {/* TABLA DE AUDITORÍAS DE CALIDAD */}
      <div className="table-container">
        <table className="calidad-table">
          <thead>
            <tr>
              <th>Orden (OP)</th>
              <th>Inspector / Auditor</th>
              <th>Muestra Auditada</th>
              <th>Prendas Defectuosas</th>
              <th>Resultado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {reportesFiltrados.map((item) => (
              <tr key={item.id}>
                <td><strong>{item.OP}</strong></td>
                <td>{item.inspector}</td>
                <td>{item.auditadas} Pzs</td>
                <td>{item.defectuosas} Pzs</td>
                <td>
                  <span className={`badge-calidad ${item.estado.toLowerCase()}`}>
                    {item.estado}
                  </span>
                </td>
                <td>
                  <div className="action-buttons">
                    <button className="btn-icon edit"><Edit2 size={16} /></button>
                    <button className="btn-icon delete"><Trash2 size={16} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* MODAL REGISTRAR AUDITORÍA */}
      {modalAbierto && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Registrar Inspección de Calidad</h3>
              <button className="btn-icon" onClick={() => setModalAbierto(false)}>
                <X size={20} color="#9ca3af" />
              </button>
            </div>

            <form onSubmit={handleGuardar} className="modal-form">
              <div className="form-group">
                <label>Orden de Producción (OP)</label>
                <div className="input-wrapper">
                  <input 
                    type="text" 
                    required 
                    placeholder="Ej: OP-2026-04"
                    value={nuevoReporte.OP}
                    onChange={(e) => setNuevoReporte({...nuevoReporte, OP: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Inspector Responsable</label>
                <div className="input-wrapper">
                  <input 
                    type="text" 
                    required 
                    placeholder="Nombre del auditor"
                    value={nuevoReporte.inspector}
                    onChange={(e) => setNuevoReporte({...nuevoReporte, inspector: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Muestra Evaluada</label>
                  <div className="input-wrapper">
                    <input 
                      type="number" 
                      required 
                      placeholder="Ej: 50"
                      value={nuevoReporte.auditadas}
                      onChange={(e) => setNuevoReporte({...nuevoReporte, auditadas: e.target.value})}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Defectos Hallados</label>
                  <div className="input-wrapper">
                    <input 
                      type="number" 
                      required 
                      placeholder="0"
                      value={nuevoReporte.defectuosas}
                      onChange={(e) => setNuevoReporte({...nuevoReporte, defectuosas: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label>Dictamen Final</label>
                <select 
                  value={nuevoReporte.estado}
                  onChange={(e) => setNuevoReporte({...nuevoReporte, estado: e.target.value})}
                >
                  <option value="Aprobado">Aprobado</option>
                  <option value="Rechazado">Rechazado</option>
                  <option value="Pendiente">Pendiente por Revisar</option>
                </select>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setModalAbierto(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-add-auditoria">
                  Guardar Reporte
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}