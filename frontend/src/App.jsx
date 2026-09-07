import './styles/variable.css';
import './styles/global.css';
import React, { useState } from 'react';
import Login from './views/Login';
import Dashboard from './views/Dashboard';
import Produccion from './views/Produccion';
import IngresoInsumos from './views/IngresoInsumos';
import FichaTecnica from './views/FichaTecnica';
import Calidad from './views/Calidad';
import GestionEmpleados from './views/GestionEmpleados';


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
    <div style={{ display: 'flex', minHeight: '100vh', width: '100vw', backgroundColor: '#050505', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      
      {/* SIDEBAR NEGRO/DORADO */}
      <aside style={{ 
        width: '260px', 
        backgroundColor: '#121212', 
        color: '#ffffff', 
        display: 'flex', 
        flexDirection: 'column', 
        justify: 'space-between', 
        padding: '1.5rem 1rem',
        borderRight: '1px solid #d4af37',
        boxSizing: 'border-box'
      }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 'bold', marginBottom: '1.5rem', color: '#f59e0b', textAlign: 'center', fontFamily: 'Georgia, serif' }}>
            SIES Yullita
          </h2>
          
          <div style={{ marginBottom: '1.5rem', padding: '0.85rem', backgroundColor: '#18181b', borderRadius: '8px', border: '1px solid #374151', fontSize: '0.85rem' }}>
            <p style={{ margin: 0, fontWeight: 'bold', color: '#ffffff' }}>{usuario.empleado}</p>
            <span style={{ 
              display: 'inline-block', 
              marginTop: '0.35rem', 
              padding: '0.2rem 0.6rem', 
              borderRadius: '4px', 
              backgroundColor: esAdministrador ? 'rgba(245, 158, 11, 0.2)' : 'rgba(59, 130, 246, 0.2)', 
              color: esAdministrador ? '#f59e0b' : '#60a5fa', 
              border: `1px solid ${esAdministrador ? '#f59e0b' : '#3b82f6'}`,
              fontSize: '0.75rem', 
              fontWeight: 'bold',
              textTransform: 'uppercase' 
            }}>
              {usuario.rol}
            </span>
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {esAdministrador && (
              <>
                <button
                  onClick={() => setVistaActual('dashboard')}
                  style={{
                    textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid', cursor: 'pointer', fontWeight: 'bold',
                    borderColor: vistaActual === 'dashboard' ? '#d4af37' : 'transparent',
                    backgroundColor: vistaActual === 'dashboard' ? '#f59e0b' : 'transparent', 
                    color: vistaActual === 'dashboard' ? '#000000' : '#e5e7eb',
                    transition: 'all 0.2s ease'
                  }}
                >
                  📊 Dashboard
                </button>

                <button
                  onClick={() => setVistaActual('empleados')}
                  style={{
                    textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid', cursor: 'pointer', fontWeight: 'bold',
                    borderColor: vistaActual === 'empleados' ? '#d4af37' : 'transparent',
                    backgroundColor: vistaActual === 'empleados' ? '#f59e0b' : 'transparent', 
                    color: vistaActual === 'empleados' ? '#000000' : '#e5e7eb',
                    transition: 'all 0.2s ease'
                  }}
                >
                  👥 Empleados
                </button>
              </>
            )}

            <button
              onClick={() => setVistaActual('produccion')}
              style={{
                textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid', cursor: 'pointer', fontWeight: 'bold',
                borderColor: vistaActual === 'produccion' ? '#d4af37' : 'transparent',
                backgroundColor: vistaActual === 'produccion' ? '#f59e0b' : 'transparent', 
                color: vistaActual === 'produccion' ? '#000000' : '#e5e7eb',
                transition: 'all 0.2s ease'
              }}
            >
              🧵 Producción
            </button>

            <button
              onClick={() => setVistaActual('insumos')}
              style={{
                textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid', cursor: 'pointer', fontWeight: 'bold',
                borderColor: vistaActual === 'insumos' ? '#d4af37' : 'transparent',
                backgroundColor: vistaActual === 'insumos' ? '#f59e0b' : 'transparent', 
                color: vistaActual === 'insumos' ? '#000000' : '#e5e7eb',
                transition: 'all 0.2s ease'
              }}
            >
              📦 Ingreso Insumos
            </button>

            <button
              onClick={() => setVistaActual('ficha')}
              style={{
                textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid', cursor: 'pointer', fontWeight: 'bold',
                borderColor: vistaActual === 'ficha' ? '#d4af37' : 'transparent',
                backgroundColor: vistaActual === 'ficha' ? '#f59e0b' : 'transparent', 
                color: vistaActual === 'ficha' ? '#000000' : '#e5e7eb',
                transition: 'all 0.2s ease'
              }}
            >
              📋 Ficha Técnica
            </button>

            <button
              onClick={() => setVistaActual('calidad')}
              style={{
                textAlign: 'left', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid', cursor: 'pointer', fontWeight: 'bold',
                borderColor: vistaActual === 'calidad' ? '#d4af37' : 'transparent',
                backgroundColor: vistaActual === 'calidad' ? '#f59e0b' : 'transparent', 
                color: vistaActual === 'calidad' ? '#000000' : '#e5e7eb',
                transition: 'all 0.2s ease'
              }}
            >
              ✅ Control Calidad
            </button>
          </nav>
        </div>

        <button
          onClick={handleLogout}
          style={{ 
            width: '100%', 
            padding: '0.75rem', 
            background: 'linear-gradient(135deg, #991b1b 0%, #ef4444 100%)', 
            color: '#ffffff', 
            border: '1px solid #f87171', 
            borderRadius: '8px', 
            fontWeight: 'bold', 
            cursor: 'pointer' 
          }}
        >
          🚪 Cerrar Sesión
        </button>
      </aside>

      {/* CONTENIDO PRINCIPAL CON FORZADO DE ALTURA */}
  <main style={{ flex: 1, display: 'flex', flexDirection: 'column', backgroundColor: '#050505', minHeight: '100vh', width: '100%' }}>
  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%' }}>
    {vistaActual === 'dashboard' && esAdministrador && <Dashboard user={usuario} />}
    {vistaActual === 'empleados' && esAdministrador && <GestionEmpleados usuario={usuario} />}
    {vistaActual === 'produccion' && <Produccion usuario={usuario} />}
    {vistaActual === 'insumos' && <IngresoInsumos usuario={usuario} />}
    {vistaActual === 'ficha' && <FichaTecnica usuario={usuario} />}
    {vistaActual === 'calidad' && <Calidad usuario={usuario} />}
  </div>
</main>

    </div>
  );
}