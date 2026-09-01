import { useState, useEffect } from 'react';

export default function GestionEmpleados() {
  const [empleados, setEmpleados] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });

  // Cargar lista de empleados dentro de useEffect limpiamente
  useEffect(() => {
    let montado = true;

    const cargarDatos = async () => {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/auth/usuarios');
        const data = await res.json();
        if (montado) {
          if (res.ok) {
            setEmpleados(data);
          } else {
            setMensaje({ texto: data.error || 'Error al cargar empleados', tipo: 'error' });
          }
        }
      } catch {
        if (montado) {
          setMensaje({ texto: 'No se pudo conectar con el servidor', tipo: 'error' });
        }
      } finally {
        if (montado) {
          setCargando(false);
        }
      }
    };

    cargarDatos();

    return () => {
      montado = false;
    };
  }, []);

  // Función para eliminar empleado
  const handleEliminar = async (id, nombre) => {
    const confirmar = window.confirm(`¿Estás seguro de que deseas eliminar al empleado "${nombre}"?`);
    if (!confirmar) return;

    try {
      const res = await fetch(`http://127.0.0.1:5000/api/auth/usuarios/${id}`, {
        method: 'DELETE'
      });
      const data = await res.json();

      if (res.ok) {
        setMensaje({ texto: `Empleado ${nombre} eliminado exitosamente.`, tipo: 'exito' });
        setEmpleados((prev) => prev.filter((emp) => emp.id !== id));
      } else {
        setMensaje({ texto: data.error || 'No se pudo eliminar el empleado', tipo: 'error' });
      }
    } catch {
      setMensaje({ texto: 'Error de conexión al intentar eliminar', tipo: 'error' });
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', backgroundColor: '#fff', padding: '2rem', borderRadius: '10px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
      <h2 style={{ color: '#1e293b', marginBottom: '0.5rem' }}>👥 Gestión de Empleados</h2>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>Administración de personal registrado en la plataforma SIES Creaciones Yullita.</p>

      {/* Tarjeta con total de empleados */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ backgroundColor: '#e0f2fe', padding: '1rem 1.5rem', borderRadius: '8px', borderLeft: '5px solid #0284c7' }}>
          <span style={{ fontSize: '0.85rem', color: '#0369a1', fontWeight: 'bold' }}>TOTAL REGISTRADOS</span>
          <h3 style={{ fontSize: '1.8rem', margin: '0.2rem 0 0 0', color: '#0c4a6e' }}>{empleados.length} Empleados</h3>
        </div>
      </div>

      {mensaje.texto && (
        <div style={{
          padding: '0.75rem 1rem', borderRadius: '6px', marginBottom: '1rem', fontWeight: 'bold',
          backgroundColor: mensaje.tipo === 'exito' ? '#dcfce7' : '#fee2e2',
          color: mensaje.tipo === 'exito' ? '#15803d' : '#b91c1c'
        }}>
          {mensaje.texto}
        </div>
      )}

      {/* Tabla de Empleados */}
      {cargando ? (
        <p style={{ textAlign: 'center', color: '#64748b' }}>Cargando empleados...</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: '#f1f5f9', borderBottom: '2px solid #cbd5e1', color: '#334155' }}>
                <th style={{ padding: '0.75rem' }}>ID</th>
                <th style={{ padding: '0.75rem' }}>Empleado</th>
                <th style={{ padding: '0.75rem' }}>Cédula</th>
                <th style={{ padding: '0.75rem' }}>Correo</th>
                <th style={{ padding: '0.75rem' }}>Rol</th>
                <th style={{ padding: '0.75rem', textAlign: 'center' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {empleados.map((emp) => (
                <tr key={emp.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                  <td style={{ padding: '0.75rem' }}>{emp.id}</td>
                  <td style={{ padding: '0.75rem', fontWeight: 'bold', color: '#1e293b' }}>{emp.empleado}</td>
                  <td style={{ padding: '0.75rem' }}>{emp.cedula || 'N/A'}</td>
                  <td style={{ padding: '0.75rem' }}>{emp.correo}</td>
                  <td style={{ padding: '0.75rem' }}>
                    <span style={{
                      padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold',
                      backgroundColor: emp.id_rol === 1 ? '#dcfce7' : '#dbeafe',
                      color: emp.id_rol === 1 ? '#15803d' : '#1e40af',
                      textTransform: 'uppercase'
                    }}>
                      {emp.rol}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                    {emp.id_rol !== 1 ? (
                      <button
                        onClick={() => handleEliminar(emp.id, emp.empleado)}
                        style={{ backgroundColor: '#ef4444', color: '#fff', border: 'none', padding: '0.4rem 0.75rem', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}
                      >
                        🗑️ Eliminar
                      </button>
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Protegido</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}