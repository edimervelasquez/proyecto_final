const NAVIGATION_ITEMS = [
  { id: 'produccion', label: '🧵 Producción' },
  { id: 'insumos', label: '📦 Ingreso Insumos' },
  { id: 'ficha', label: '📋 Ficha Técnica' },
  { id: 'calidad', label: '✅ Control Calidad' },
];

const ADMIN_ITEMS = [
  { id: 'dashboard', label: '📊 Dashboard' },
  { id: 'empleados', label: '👥 Empleados' },
];

const isAdmin = (user) =>
  user.rol === 'jefe' || user.rol === 'administrador' || user.id_rol === 1;

export default function AppLayout({ user, currentView, onNavigate, onLogout, children }) {
  const admin = isAdmin(user);
  const items = admin ? [...ADMIN_ITEMS, ...NAVIGATION_ITEMS] : NAVIGATION_ITEMS;

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div>
          <h2 className="app-brand">SIES Yullita</h2>
          <div className="user-card">
            <strong>{user.empleado}</strong>
            <span className={`user-role ${admin ? 'user-role-admin' : ''}`}>
              {user.rol}
            </span>
          </div>
          <nav className="app-navigation" aria-label="Navegación principal">
            {items.map((item) => (
              <button
                key={item.id}
                className={`navigation-button ${currentView === item.id ? 'active' : ''}`}
                onClick={() => onNavigate(item.id)}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
        <button className="logout-button" onClick={onLogout}>
          🚪 Cerrar Sesión
        </button>
      </aside>
      <main className="app-content">{children}</main>
    </div>
  );
}
