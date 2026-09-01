import { useState } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Produccion from './components/Produccion';
import IngresoInsumos from './components/IngresoInsumos';
import FichaTecnica from './components/FichaTecnica';
import Calidad from './components/Calidad';
import GestionEmpleados from './components/GestionEmpleados'; // <- Importar nuevo componente

export default function App() {
  const [usuario, setUsuario] = useState(null);
  const [vistaActual, setVistaActual] = useState('produccion');

  const handleLoginSuccess = (dataRecibida) => {
    const datosUsuario = dataRecibida.usuario || dataRecibida;
    const rolFormateado = (datosUsuario.rol || datosUsuario.nombre_rol || 'trabajador').toString().toLowerCase();

    const usuarioValido = {
      ...datosUsuario,
      id_usuario: datosUsuario.id_usuario || datosUsuario.id,
      empleado: datosUsuario.empleado || datosUsuario.nombre || 'Usuario SIES',
      correo_usuario: datosUsuario.correo_usuario || datosUsuario.correo,
      rol: rolFormateado
    };

    setUsuario(usuarioValido);

    if (rolFormateado === 'jefe' || rolFormateado === 'administrador' || datosUsuario.id_rol === 1) {
      setVistaActual('dashboard');
    } else {
      setVistaActual('produccion');
    }
  };

  const handleLogout = () => {
    setUsuario(null);
    setVistaActual('produccion');
  };

  if (!usuario) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const esAdministrador = usuario.rol === 'jefe' || usuario.rol === 'administrador' || usuario.id_rol === 1;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f4f6f9', fontFamily: 'sans-serif' }}>
      
      {/* SIDEBAR */}
      <aside style={{ width: '250px', backgroundColor: '#1e293b', color: '#fff', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '1.5rem 1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1.5rem', color: '#38bdf8', textAlign: 'center' }}>
            SIES Yullita
          </h2>
          
          <div style={{ marginBottom: '1.5rem', padding: '0.75rem', backgroundColor: '#334155', borderRadius: '8px', fontSize: '0.85rem' }}>
            <p style={{ margin: 0, fontWeight: 'bold' }}>{usuario.empleado}</p>
            <span style={{ display: 'inline-block', marginTop: '0.25rem', padding: '0.2rem 0.5rem', borderRadius: '4px', backgroundColor: esAdministrador ? '#16a34a' : '#2563eb', color: '#fff', fontSize: '0.75rem', textTransform: 'uppercase' }}>
              {usuario.rol}
            </span>
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {/* Opciones exclusivas del Jefe/Administrador */}
            {esAdministrador && (
              <>
                <button
                  onClick={() => setVistaActual('dashboard')}
                  style={{
                    textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold',
                    backgroundColor: vistaActual === 'dashboard' ? '#0284c7' : 'transparent', color: '#fff'
                  }}
                >
                  📊 Dashboard
                </button>

                <button
                  onClick={() => setVistaActual('empleados')}
                  style={{
                    textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold',
                    backgroundColor: vistaActual === 'empleados' ? '#0284c7' : 'transparent', color: '#fff'
                  }}
                >
                  👥 Empleados
                </button>
              </>
            )}

            <button
              onClick={() => setVistaActual('produccion')}
              style={{
                textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold',
                backgroundColor: vistaActual === 'produccion' ? '#0284c7' : 'transparent', color: '#fff'
              }}
            >
              🧵 Producción
            </button>

            <button
              onClick={() => setVistaActual('insumos')}
              style={{
                textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold',
                backgroundColor: vistaActual === 'insumos' ? '#0284c7' : 'transparent', color: '#fff'
              }}
            >
              📦 Ingreso Insumos
            </button>

            <button
              onClick={() => setVistaActual('ficha')}
              style={{
                textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold',
                backgroundColor: vistaActual === 'ficha' ? '#0284c7' : 'transparent', color: '#fff'
              }}
            >
              📋 Ficha Técnica
            </button>

            <button
              onClick={() => setVistaActual('calidad')}
              style={{
                textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: 'bold',
                backgroundColor: vistaActual === 'calidad' ? '#0284c7' : 'transparent', color: '#fff'
              }}
            >
              ✅ Control Calidad
            </button>
          </nav>
        </div>

        <button
          onClick={handleLogout}
          style={{ width: '100%', padding: '0.75rem', backgroundColor: '#dc2626', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}
        >
          🚪 Cerrar Sesión
        </button>
      </aside>

      {/* CONTENIDO PRINCIPAL */}
      <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
        {vistaActual === 'dashboard' && esAdministrador && <Dashboard usuario={usuario} onLogout={handleLogout} />}
        {vistaActual === 'empleados' && esAdministrador && <GestionEmpleados />}
        {vistaActual === 'produccion' && <Produccion usuario={usuario} />}
        {vistaActual === 'insumos' && <IngresoInsumos usuario={usuario} />}
        {vistaActual === 'ficha' && <FichaTecnica usuario={usuario} />}
        {vistaActual === 'calidad' && <Calidad usuario={usuario} />}
      </main>

    </div>
  );
}