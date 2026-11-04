import { useState } from 'react';
import { AUTH_STORAGE_KEY } from '../config/api';
import AppLayout from '../layouts/AppLayout';
import Calidad from '../pages/quality/Calidad';
import Dashboard from '../pages/dashboard/Dashboard';
import FichaTecnica from '../pages/inventory/FichaTecnica';
import IngresoInsumos from '../pages/inventory/IngresoInsumos';
import InventarioPrendas from '../pages/inventory/InventarioPrendas';
import Ventas from '../pages/inventory/Ventas';
import Login from '../pages/auth/Login';
import GestionEmpleados from '../pages/users/GestionEmpleados';
import Produccion from '../pages/production/Produccion';
import '../styles/variable.css';
import '../styles/global.css';
import '../styles/theme.css';

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
    auth?.usuario?.id_rol === 1
      ? 'dashboard'
      : auth?.usuario?.id_rol === 3
        ? 'ventas'
        : 'produccion',
  );

  const handleLoginSuccess = (data) => {
    const nextAuth = { ...data, usuario: normalizeUser(data) };
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(nextAuth));
    setAuth(nextAuth);
    setCurrentView(
      nextAuth.usuario.id_rol === 1
        ? 'dashboard'
        : nextAuth.usuario.id_rol === 3
          ? 'ventas'
          : 'produccion',
    );
  };

  const handleLogout = () => {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    setAuth(null);
    setCurrentView('produccion');
  };

  if (!auth?.usuario) return <Login onLoginSuccess={handleLoginSuccess} />;

  const user = auth.usuario;
  const admin = user.rol === 'jefe' || user.rol === 'administrador' || user.id_rol === 1;
  const vendedor = user.id_rol === 3;
  const views = {
    dashboard: admin ? <Dashboard user={user} /> : null,
    empleados: admin ? <GestionEmpleados user={user} /> : null,
    produccion: !vendedor ? <Produccion user={user} /> : null,
    insumos: !vendedor ? <IngresoInsumos user={user} /> : null,
    ficha: !vendedor ? <FichaTecnica user={user} /> : null,
    calidad: !vendedor ? <Calidad user={user} /> : null,
    inventario: <InventarioPrendas user={user} />,
    ventas: <Ventas user={user} />,
  };

  return (
    <AppLayout
      user={user}
      currentView={currentView}
      onNavigate={setCurrentView}
      onLogout={handleLogout}
    >
      {views[currentView] || (vendedor ? views.ventas : views.produccion)}
    </AppLayout>
  );
}
