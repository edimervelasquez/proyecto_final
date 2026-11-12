const NAVIGATION_ITEMS = [
  { id: 'produccion', label: '🧵 Producción' },
  { id: 'mermas', label: '♻️ Mermas' },
  { id: 'insumos', label: '📦 Ingreso Insumos' },
  { id: 'ficha', label: '📋 Ficha Técnica' },
  { id: 'calidad', label: '✅ Control Calidad' },
];

const ADMIN_ITEMS = [
  { id: 'dashboard', label: '📊 Dashboard' },
  { id: 'empleados', label: '👥 Empleados' },
  { id: 'inventario', label: '👕 Inventario Prendas' },
  { id: 'ventas', label: '💰 Ventas' },
];

const SALES_ITEMS = [
  { id: 'inventario', label: '👕 Prendas y Precios' },
  { id: 'ventas', label: '💰 Registrar Ventas' },
];

const isAdmin = (user) =>
  user.rol === 'jefe' || user.rol === 'administrador' || user.id_rol === 1;

export default function AppLayout({ user, currentView, onNavigate, onLogout, children }) {
  const admin = isAdmin(user);
  const vendedor = user.id_rol === 3;
  const items = admin
    ? [...ADMIN_ITEMS, ...NAVIGATION_ITEMS]
    : vendedor
      ? SALES_ITEMS
      : NAVIGATION_ITEMS;

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
