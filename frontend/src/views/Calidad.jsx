import { useState } from 'react';
import { Plus, Search, Edit2, Trash2, X } from 'lucide-react';
import '../styles/components/Calidad.css';

export default function Calidad() {
  const [busqueda, setBusqueda] = useState('');
  const [modalAbierto, setModalAbierto] = useState(false);
  const [modoEdicion, setModoEdicion] = useState(false);
  const [reporteEditarId, setReporteEditarId] = useState(null);

  // Datos de prueba iniciales
  const [reportes, setReportes] = useState([
    { id: 1, OP: 'OP-2026-01', inspector: 'Carlos Ruiz', auditadas: 100, defectuosas: 2, estado: 'Aprobado' },
    { id: 2, OP: 'OP-2026-02', inspector: 'Ana Gomez', auditadas: 50, defectuosas: 8, estado: 'Rechazado' },
    { id: 3, OP: 'OP-2026-03', inspector: 'Carlos Ruiz', auditadas: 30, defectuosas: 0, estado: 'Pendiente' },
  ]);

  const [formReporte, setFormReporte] = useState({
    OP: '',
    inspector: '',
    auditadas: '',
    defectuosas: '',
    estado: 'Aprobado'
  });

  // Abrir modal para Crear
  const handleAbrirCrear = () => {
    setModoEdicion(false);
    setReporteEditarId(null);
    setFormReporte({ OP: '', inspector: '', auditadas: '', defectuosas: '', estado: 'Aprobado' });
    setModalAbierto(true);
  };

  // Abrir modal para Editar
  const handleAbrirEditar = (item) => {
    setModoEdicion(true);
    setReporteEditarId(item.id);
    setFormReporte({
      OP: item.OP,
      inspector: item.inspector,
      auditadas: item.auditadas,
      defectuosas: item.defectuosas,
      estado: item.estado
    });
    setModalAbierto(true);
  };

  // Función para Eliminar
  const handleEliminar = (id) => {
    if (window.confirm("¿Estás seguro de que deseas eliminar este reporte de calidad?")) {
      setReportes(reportes.filter(item => item.id !== id));
    }
  };

  // Guardar (Crear o Actualizar)
  const handleGuardar = (e) => {
    e.preventDefault();

    if (modoEdicion) {
      setReportes(reportes.map(item => 
        item.id === reporteEditarId ? { ...formReporte, id: reporteEditarId } : item
      ));
    } else {
      setReportes([...reportes, { ...formReporte, id: Date.now() }]);
    }

    setModalAbierto(false);
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

        <button className="btn-add-auditoria" onClick={handleAbrirCrear}>
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
                    <button 
                      className="btn-icon edit"
                      onClick={() => handleAbrirEditar(item)}
                      title="Editar Reporte"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button 
                      className="btn-icon delete"
                      onClick={() => handleEliminar(item.id)}
                      title="Eliminar Reporte"
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

      {/* MODAL REGISTRAR / EDITAR AUDITORÍA */}
      {modalAbierto && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>{modoEdicion ? 'Editar Inspección de Calidad' : 'Registrar Inspección de Calidad'}</h3>
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
                    value={formReporte.OP}
                    onChange={(e) => setFormReporte({...formReporte, OP: e.target.value})}
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
                    value={formReporte.inspector}
                    onChange={(e) => setFormReporte({...formReporte, inspector: e.target.value})}
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
                      value={formReporte.auditadas}
                      onChange={(e) => setFormReporte({...formReporte, auditadas: e.target.value})}
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
                      value={formReporte.defectuosas}
                      onChange={(e) => setFormReporte({...formReporte, defectuosas: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label>Dictamen Final</label>
                <select 
                  value={formReporte.estado}
                  onChange={(e) => setFormReporte({...formReporte, estado: e.target.value})}
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
                  {modoEdicion ? 'Actualizar Reporte' : 'Guardar Reporte'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}