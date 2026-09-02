import { useState } from 'react';
import { UserPlus, Search, Edit2, Trash2, X } from 'lucide-react';
import '../styles/components/GestionEmpleados.css';

export default function GestionEmpleados() {
  const [busqueda, setBusqueda] = useState('');
  const [modalAbierto, setModalAbierto] = useState(false);

  // Datos de prueba iniciales
  const [empleados, setEmpleados] = useState([
    { id: 1, documento: '1012345678', nombre: 'Jhorman Martinez', cargo: 'Operario de Corte', telefono: '3101234567', estado: 'Activo' },
    { id: 2, documento: '1098765432', nombre: 'Maria Fernanda', cargo: 'Inspectora de Calidad', telefono: '3209876543', estado: 'Activo' },
    { id: 3, documento: '1055443322', nombre: 'Andres Cepeda', cargo: 'Confeccionista', telefono: '3155544332', estado: 'Inactivo' },
  ]);

  const [nuevoEmpleado, setNuevoEmpleado] = useState({
    documento: '',
    nombre: '',
    cargo: 'Operario de Corte',
    telefono: '',
    estado: 'Activo'
  });

  const handleGuardar = (e) => {
    e.preventDefault();
    setEmpleados([...empleados, { ...nuevoEmpleado, id: Date.now() }]);
    setModalAbierto(false);
    setNuevoEmpleado({ documento: '', nombre: '', cargo: 'Operario de Corte', telefono: '', estado: 'Activo' });
  };

  const empleadosFiltrados = empleados.filter(e => 
    e.nombre.toLowerCase().includes(busqueda.toLowerCase()) || 
    e.documento.includes(busqueda) ||
    e.cargo.toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div className="empleados-container">
      {/* BARRA SUPERIOR DE ACCIONES */}
      <div className="empleados-header-actions">
        <div className="search-box">
          <Search size={18} color="#f59e0b" />
          <input 
            type="text" 
            placeholder="Buscar por Nombre, Cédula o Cargo..." 
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <button className="btn-add-empleado" onClick={() => setModalAbierto(true)}>
          <UserPlus size={18} />
          Nuevo Empleado
        </button>
      </div>

      {/* TABLA DE EMPLEADOS */}
      <div className="table-container">
        <table className="empleados-table">
          <thead>
            <tr>
              <th>Documento (CC)</th>
              <th>Nombre Completo</th>
              <th>Cargo / Rol</th>
              <th>Teléfono Contacto</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empleadosFiltrados.map((item) => (
              <tr key={item.id}>
                <td><strong>{item.documento}</strong></td>
                <td>{item.nombre}</td>
                <td>{item.cargo}</td>
                <td>{item.telefono}</td>
                <td>
                  <span className={`badge-empleado ${item.estado.toLowerCase()}`}>
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

      {/* MODAL REGISTRAR EMPLEADO */}
      {modalAbierto && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Registrar Nuevo Empleado</h3>
              <button className="btn-icon" onClick={() => setModalAbierto(false)}>
                <X size={20} color="#9ca3af" />
              </button>
            </div>

            <form onSubmit={handleGuardar} className="modal-form">
              <div className="form-group">
                <label>Número de Documento</label>
                <div className="input-wrapper">
                  <input 
                    type="text" 
                    required 
                    placeholder="Ej: 1012345678"
                    value={nuevoEmpleado.documento}
                    onChange={(e) => setNuevoEmpleado({...nuevoEmpleado, documento: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Nombre Completo</label>
                <div className="input-wrapper">
                  <input 
                    type="text" 
                    required 
                    placeholder="Ej: Juan Perez"
                    value={nuevoEmpleado.nombre}
                    onChange={(e) => setNuevoEmpleado({...nuevoEmpleado, nombre: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Teléfono</label>
                  <div className="input-wrapper">
                    <input 
                      type="text" 
                      required 
                      placeholder="Ej: 3001234567"
                      value={nuevoEmpleado.telefono}
                      onChange={(e) => setNuevoEmpleado({...nuevoEmpleado, telefono: e.target.value})}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Estado</label>
                  <select 
                    value={nuevoEmpleado.estado}
                    onChange={(e) => setNuevoEmpleado({...nuevoEmpleado, estado: e.target.value})}
                  >
                    <option value="Activo">Activo</option>
                    <option value="Inactivo">Inactivo</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Cargo</label>
                <select 
                  value={nuevoEmpleado.cargo}
                  onChange={(e) => setNuevoEmpleado({...nuevoEmpleado, cargo: e.target.value})}
                >
                  <option value="Operario de Corte">Operario de Corte</option>
                  <option value="Confeccionista">Confeccionista</option>
                  <option value="Inspectora de Calidad">Inspectora de Calidad</option>
                  <option value="Supervisor de Taller">Supervisor de Taller</option>
                </select>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setModalAbierto(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-add-empleado">
                  Guardar Empleado
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}