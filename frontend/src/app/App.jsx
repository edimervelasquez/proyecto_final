import { useState } from 'react';
import { AUTH_STORAGE_KEY } from '../config/api';
import AppLayout from '../layouts/AppLayout';
import Calidad from '../pages/quality/Calidad';
import Dashboard from '../pages/dashboard/Dashboard';
import FichaTecnica from '../pages/inventory/FichaTecnica';
import IngresoInsumos from '../pages/inventory/IngresoInsumos';
import Login from '../pages/auth/Login';
import GestionEmpleados from '../pages/users/GestionEmpleados';
import Produccion from '../pages/production/Produccion';
import '../styles/variable.css';
import '../styles/global.css';

const normalizeUser = (data) => {
  const user = data.usuario || data;
  return {
    ...user,
    id_usuario: user.id_usuario || user.id,
    empleado: user.empleado || user.nombre || 'Usuario SIES',
    correo_usuario: user.correo_usuario || user.correo,
    rol: (user.rol || user.nombre_rol || 'trabajador').toString().toLowerCase(),
  };
};

const getInitialAuth = () => {
  try {
    return JSON.parse(localStorage.getItem(AUTH_STORAGE_KEY) || 'null');
  } catch {
    return null;
  }
};

export default function App() {
  const [auth, setAuth] = useState(getInitialAuth);
  const [currentView, setCurrentView] = useState(
    auth?.usuario?.rol === 'administrador' ? 'dashboard' : 'produccion',
  );

  const handleLoginSuccess = (data) => {
    const nextAuth = { ...data, usuario: normalizeUser(data) };
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(nextAuth));
    setAuth(nextAuth);
    setCurrentView(nextAuth.usuario.id_rol === 1 ? 'dashboard' : 'produccion');
  };

  const handleLogout = () => {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    setAuth(null);
    setCurrentView('produccion');
  };

  if (!auth?.usuario) return <Login onLoginSuccess={handleLoginSuccess} />;

  const user = auth.usuario;
  const admin = user.rol === 'jefe' || user.rol === 'administrador' || user.id_rol === 1;
  const views = {
    dashboard: admin ? <Dashboard user={user} /> : null,
    empleados: admin ? <GestionEmpleados user={user} /> : null,
    produccion: <Produccion user={user} />,
    insumos: <IngresoInsumos user={user} />,
    ficha: <FichaTecnica user={user} />,
    calidad: <Calidad user={user} />,
  };

  return (
    <AppLayout
      user={user}
      currentView={currentView}
      onNavigate={setCurrentView}
      onLogout={handleLogout}
    >
      {views[currentView] || views.produccion}
    </AppLayout>
  );
}
