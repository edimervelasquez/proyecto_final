import { useEffect, useState } from 'react';
import {
  BadgeCheck,
  Factory,
  LayoutDashboard,
  LogOut,
  Menu,
  PackagePlus,
  Recycle,
  Shirt,
  Users,
  Wallet,
  ClipboardList,
  X,
} from 'lucide-react';
import HangerIcon from '../components/HangerIcon';

const NAVIGATION_ITEMS = [
  { id: 'produccion', label: 'Producción', Icon: Factory },
  { id: 'mermas', label: 'Mermas', Icon: Recycle },
  { id: 'insumos', label: 'Ingreso Insumos', Icon: PackagePlus },
  { id: 'ficha', label: 'Ficha Técnica', Icon: ClipboardList },
  { id: 'calidad', label: 'Control Calidad', Icon: BadgeCheck },
];

const ADMIN_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', Icon: LayoutDashboard },
  { id: 'empleados', label: 'Empleados', Icon: Users },
  { id: 'inventario', label: 'Inventario Prendas', Icon: Shirt },
  { id: 'ventas', label: 'Ventas', Icon: Wallet },
];

const SALES_ITEMS = [
  { id: 'inventario', label: 'Prendas y Precios', Icon: Shirt },
  { id: 'ventas', label: 'Registrar Ventas', Icon: Wallet },
];

const isAdmin = (user) =>
  user.rol === 'jefe' || user.rol === 'administrador' || user.id_rol === 1;

export default function AppLayout({ user, currentView, onNavigate, onLogout, children }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const admin = isAdmin(user);
  const vendedor = user.id_rol === 3;
  const items = admin
    ? [...ADMIN_ITEMS, ...NAVIGATION_ITEMS]
    : vendedor
      ? SALES_ITEMS
      : NAVIGATION_ITEMS;

  useEffect(() => {
    if (!menuOpen) return undefined;

    const closeOnEscape = (event) => {
      if (event.key === 'Escape') setMenuOpen(false);
    };
    document.addEventListener('keydown', closeOnEscape);
    return () => document.removeEventListener('keydown', closeOnEscape);
  }, [menuOpen]);

  const brand = (
    <>
      <HangerIcon size={28} />
      <span className="app-brand-wordmark">
        <strong><span>S</span>IES</strong>
        <small>Yullita</small>
      </span>
    </>
  );

  return (
    <div className="app-shell">
      <header className="mobile-topbar">
        <div className="mobile-brand">{brand}</div>
        <button
          type="button"
          className="menu-toggle"
          aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
          aria-expanded={menuOpen}
          aria-controls="app-navigation-drawer"
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </header>
      {menuOpen && (
        <button
          type="button"
          className="drawer-overlay"
          aria-label="Cerrar menú de navegación"
          onClick={() => setMenuOpen(false)}
        />
      )}
      <aside
        id="app-navigation-drawer"
        className={`app-sidebar ${menuOpen ? 'is-open' : ''}`}
        aria-label="Menú principal"
      >
        <div>
          <div className="app-brand">{brand}</div>
          <div className="user-card">
            <strong>{user.empleado}</strong>
            <span className={`user-role ${admin ? 'user-role-admin' : ''}`}>
              {user.rol}
            </span>
          </div>
          <nav className="app-navigation" aria-label="Navegación principal">
            {items.map((item) => (
              <button
                type="button"
                key={item.id}
                className={`navigation-button ${currentView === item.id ? 'active' : ''}`}
                onClick={() => {
                  onNavigate(item.id);
                  setMenuOpen(false);
                }}
              >
                <item.Icon size={19} strokeWidth={1.8} aria-hidden="true" />
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
        </div>
        <button
          type="button"
          className="logout-button"
          onClick={() => {
            setMenuOpen(false);
            onLogout();
          }}
        >
          <LogOut size={19} strokeWidth={1.8} aria-hidden="true" />
          <span>Cerrar Sesión</span>
        </button>
      </aside>
      <main className="app-content">{children}</main>
    </div>
  );
}
