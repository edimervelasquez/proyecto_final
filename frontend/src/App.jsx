import { useState,  } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { LayoutDashboard, PackagePlus, ClipboardList, Scissors, ShieldCheck, LogOut, User } from 'lucide-react';

// Importación de tus componentes creados
import Dashboard from './components/Dashboard';
import IngresoInsumos from './components/IngresoInsumos';
import FichaTecnica from './components/FichaTecnica';
import Produccion from './components/Produccion';
import Calidad from './components/Calidad';
import Login from './components/Login'; // <-- Nuevo import

export default function App() {
  // Inicialización directa y limpia
  const [user, setUser] = useState(() => {
    const loggedUser = localStorage.getItem('sies_user');
    return loggedUser ? JSON.parse(loggedUser) : null;
  });

  const handleLogout = () => {
    localStorage.removeItem('sies_user');
    setUser(null);
    window.location.href = '/';
  };

  // Si no está logueado, se muestra la pantalla de Login de forma obligatoria
  if (!user) {
    return <Login onLoginSuccess={(usuario) => setUser(usuario)} />;
  }

  return (
    // ... Todo el resto de tu código de rutas permanece exactamente igual ...
    <Router>
      <div style={styles.appContainer}>
        
        {/* SIDEBAR LATERAL DINÁMICO */}
        <aside style={styles.sidebar}>
          <div style={styles.logoArea}>
            <ShieldCheck size={24} color="#ffffff" />
            <h2 style={styles.logoText}>Yullita ERP</h2>
          </div>

          {/* CUADRO INFORMACIÓN DEL USUARIO */}
          <div style={styles.userBadge}>
            <User size={16} color="#9ca3af" />
            <div>
              <p style={styles.userName}>{user.nombre}</p>
              <p style={styles.userRole}>{user.rol.toUpperCase()}</p>
            </div>
          </div>

          <nav style={styles.navMenu}>
            {/* VISTAS EXCLUSIVAS DEL JEFE */}
            {user.rol === 'jefe' && (
              <>
                <Link to="/" style={styles.navLink}>
                  <LayoutDashboard size={18} /> Dashboard
                </Link>
                <Link to="/ficha-tecnica" style={styles.navLink}>
                  <Scissors size={18} /> Ficha Técnica
                </Link>
              </>
            )}

            {/* VISTAS COMUNES / TRABAJADOR */}
            <Link to="/insumos" style={styles.navLink}>
              <PackagePlus size={18} /> Carga Insumos
            </Link>
            <Link to="/produccion" style={styles.navLink}>
              <ClipboardList size={18} /> Orden Producción
            </Link>
            <Link to="/calidad" style={styles.navLink}>
              <ShieldCheck size={18} /> Control Calidad
            </Link>
          </nav>

          {/* BOTÓN SALIR SEGURA */}
          <button onClick={handleLogout} style={styles.logoutBtn}>
            <LogOut size={18} /> Cerrar Sesión
          </button>
        </aside>

        {/* CONTENIDO PRINCIPAL */}
        <main style={styles.mainContent}>
          <Routes>
            {user.rol === 'jefe' && (
              <>
                <Route path="/" element={<Dashboard />} />
                <Route path="/ficha-tecnica" element={<FichaTecnica />} />
              </>
            )}
            <Route path="/insumos" element={<IngresoInsumos />} />
            <Route path="/produccion" element={<Produccion />} />
            <Route path="/calidad" element={<Calidad />} />
            {/* Redirección por defecto si un trabajador intenta forzar la barra del navegador */}
            <Route path="*" element={user.rol === 'jefe' ? <Dashboard /> : <Produccion />} />
          </Routes>
        </main>

      </div>
    </Router>
  );
}

const styles = {
  appContainer: { display: 'flex', height: '100vh', width: '100vw', backgroundColor: '#f9fafb' },
  sidebar: { width: '260px', backgroundColor: '#1e293b', color: '#ffffff', padding: '20px', display: 'flex', flexDirection: 'column' },
  logoArea: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', borderBottom: '1px solid #334155', paddingBottom: '15px' },
  logoText: { fontSize: '18px', fontWeight: 'bold', margin: 0 },
  userBadge: { display: 'flex', alignItems: 'center', gap: '10px', backgroundColor: '#0f172a', padding: '10px', borderRadius: '6px', marginBottom: '20px' },
  userName: { fontSize: '13px', fontWeight: 'bold', margin: 0, color: '#f3f4f6' },
  userRole: { fontSize: '11px', color: '#10b981', margin: 0, fontWeight: 'bold' },
  navMenu: { display: 'flex', flexDirection: 'column', gap: '8px', flexGrow: 1 },
  navLink: { display: 'flex', alignItems: 'center', gap: '12px', color: '#cbd5e1', textDecoration: 'none', padding: '12px', borderRadius: '6px', fontSize: '14px', transition: 'background 0.2s' },
  logoutBtn: { display: 'flex', alignItems: 'center', gap: '12px', backgroundColor: 'transparent', border: 'none', color: '#f87171', padding: '12px', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', textAlign: 'left', marginTop: 'auto' },
  mainContent: { flexGrow: 1, padding: '40px', overflowY: 'auto' }
};