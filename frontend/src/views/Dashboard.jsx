import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Scissors, 
  CheckCircle, 
  Users, 
  User,
  UserPlus,
  Plus,
  PackagePlus,
  FileText,
  ShieldCheck,
  Edit,
  Trash2
} from 'lucide-react';
import '../styles/components/Dashboard.css';

export default function Dashboard({ user }) {
  const [moduloActivo, setModuloActivo] = useState('resumen');

  const mapearModulo = (textoMenu) => {
    const texto = textoMenu.toLowerCase().trim();
    if (texto.includes('dashboard') || texto.includes('resumen')) return 'resumen';
    if (texto.includes('ficha')) return 'ficha';
    if (texto.includes('ingreso') || texto.includes('insumo')) return 'insumos';
    if (texto.includes('producción') || texto.includes('produccion')) return 'produccion';
    if (texto.includes('control') || texto.includes('calidad')) return 'calidad';
    if (texto.includes('empleado') || texto.includes('personal')) return 'personal';
    return 'resumen';
  };

  useEffect(() => {
    const manejarClicMenu = (e) => {
      const elementoBtn = e.target.closest('button, a, li');
      if (elementoBtn) {
        const texto = elementoBtn.innerText || elementoBtn.textContent;
        if (texto) {
          const nuevoModulo = mapearModulo(texto);
          setModuloActivo(nuevoModulo);
        }
      }
    };

    document.addEventListener('click', manejarClicMenu);
    return () => {
      document.removeEventListener('click', manejarClicMenu);
    };
  }, []);

  return (
    <div className="dashboard-layout">
      {/* BARRA SUPERIOR (TOP BAR) */}
      <header className="top-bar">
        <h1>
          {moduloActivo === 'resumen' && 'Panel de Control Principal'}
          {moduloActivo === 'ficha' && 'Fichas Técnicas de Prendas'}
          {moduloActivo === 'insumos' && 'Gestión de Insumos y Materia Prima'}
          {moduloActivo === 'produccion' && 'Control de Órdenes de Producción'}
          {moduloActivo === 'calidad' && 'Auditorías de Calidad'}
          {moduloActivo === 'personal' && 'Gestión de Personal y Operarios'}
        </h1>
        
        <div className="user-badge">
          <User size={16} color="#f59e0b" />
          <span>{user?.empleado || user?.correo_usuario || 'Brandon Monsalve'}</span>
        </div>
      </header>

      {/* ÁREA DE CONTENIDO */}
      <section className="content-body">
        {/* VISTA 1: DASHBOARD / RESUMEN */}
        {moduloActivo === 'resumen' && (
          <>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-icon"><Package size={28} /></div>
                <div className="metric-info">
                  <h3>Total Insumos</h3>
                  <p>128 items</p>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon"><Scissors size={28} /></div>
                <div className="metric-info">
                  <h3>Órdenes Activas</h3>
                  <p>14 Lotes</p>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon"><CheckCircle size={28} /></div>
                <div className="metric-info">
                  <h3>Aprobación Calidad</h3>
                  <p>98.5%</p>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-icon"><Users size={28} /></div>
                <div className="metric-info">
                  <h3>Operarios en Taller</h3>
                  <p>22 Activos</p>
                </div>
              </div>
            </div>

            <div className="module-placeholder">
              <div className="dashboard-widget">
                <h3>Órdenes de Producción Recientes</h3>
                <ul className="activity-list">
                  <li className="activity-item">
                    <span><strong>OP-2026-01:</strong> Camiseta Oversize Negra (500 unid)</span>
                    <span style={{ color: '#f59e0b', fontWeight: 'bold' }}>En Corte</span>
                  </li>
                  <li className="activity-item">
                    <span><strong>OP-2026-02:</strong> Jean Slim Fit Azul (250 unid)</span>
                    <span style={{ color: '#3b82f6', fontWeight: 'bold' }}>En Confección</span>
                  </li>
                  <li className="activity-item">
                    <span><strong>OP-2026-03:</strong> Chaqueta Denim (120 unid)</span>
                    <span style={{ color: '#10b981', fontWeight: 'bold' }}>Finalizado</span>
                  </li>
                </ul>
              </div>

              <div className="dashboard-widget">
                <h3>Alertas del Sistema</h3>
                <ul className="activity-list">
                  <li className="activity-item">
                    <span>Hilo 100% Poliéster Negro</span>
                    <span style={{ color: '#ef4444', fontWeight: 'bold' }}>Stock Bajo</span>
                  </li>
                  <li className="activity-item">
                    <span>Auditoría Lote #08</span>
                    <span style={{ color: '#10b981', fontWeight: 'bold' }}>Aprobado</span>
                  </li>
                </ul>
              </div>
            </div>
          </>
        )}

        {/* VISTA 2: GESTIÓN DE EMPLEADOS */}
        {moduloActivo === 'personal' && (
          <div className="module-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <input type="text" placeholder="Buscar por Nombre, Cédula..." style={{ width: '350px', padding: '0.6rem 1rem', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#121212', color: '#fff' }} />
              <button style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', backgroundColor: '#f59e0b', color: '#000', fontWeight: 'bold', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                <UserPlus size={18} /> Nuevo Empleado
              </button>
            </div>
            <div className="table-wrapper">
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #374151', backgroundColor: '#1f2937' }}>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Documento (CC)</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Nombre Completo</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Cargo / Rol</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Teléfono Contacto</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Estado</th>
                    <th style={{ padding: '1rem', color: '#f59e0b', textAlign: 'center' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #27272a' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>1012345678</td>
                    <td style={{ padding: '1rem' }}>Jhorman Martinez</td>
                    <td style={{ padding: '1rem' }}>Operario de Corte</td>
                    <td style={{ padding: '1rem' }}>3101234567</td>
                    <td style={{ padding: '1rem' }}><span style={{ padding: '0.25rem 0.75rem', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 'bold', backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#10b981', border: '1px solid #10b981' }}>Activo</span></td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <button style={{ background: 'none', border: 'none', color: '#f59e0b', cursor: 'pointer', marginRight: '0.75rem' }}><Edit size={16} /></button>
                      <button style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}><Trash2 size={16} /></button>
                    </td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #27272a' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>1098765432</td>
                    <td style={{ padding: '1rem' }}>Maria Fernanda</td>
                    <td style={{ padding: '1rem' }}>Inspectora de Calidad</td>
                    <td style={{ padding: '1rem' }}>3209876543</td>
                    <td style={{ padding: '1rem' }}><span style={{ padding: '0.25rem 0.75rem', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 'bold', backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#10b981', border: '1px solid #10b981' }}>Activo</span></td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <button style={{ background: 'none', border: 'none', color: '#f59e0b', cursor: 'pointer', marginRight: '0.75rem' }}><Edit size={16} /></button>
                      <button style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}><Trash2 size={16} /></button>
                    </td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #27272a' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>1055443322</td>
                    <td style={{ padding: '1rem' }}>Andres Cepeda</td>
                    <td style={{ padding: '1rem' }}>Confeccionista</td>
                    <td style={{ padding: '1rem' }}>3155544332</td>
                    <td style={{ padding: '1rem' }}><span style={{ padding: '0.25rem 0.75rem', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 'bold', backgroundColor: 'rgba(239, 68, 68, 0.2)', color: '#ef4444', border: '1px solid #ef4444' }}>Inactivo</span></td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <button style={{ background: 'none', border: 'none', color: '#f59e0b', cursor: 'pointer', marginRight: '0.75rem' }}><Edit size={16} /></button>
                      <button style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}><Trash2 size={16} /></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* VISTA 3: PRODUCCIÓN */}
        {moduloActivo === 'produccion' && (
          <div className="module-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <input type="text" placeholder="Buscar por OP o Prenda..." style={{ width: '350px', padding: '0.6rem 1rem', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#121212', color: '#fff' }} />
              <button style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', backgroundColor: '#f59e0b', color: '#000', fontWeight: 'bold', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                <Plus size={18} /> Nueva Orden
              </button>
            </div>
            <div className="table-wrapper">
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #374151', backgroundColor: '#1f2937' }}>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Orden (OP)</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Prenda</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Cantidad</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Estado</th>
                    <th style={{ padding: '1rem', color: '#f59e0b', textAlign: 'center' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #27272a' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>OP-2026-01</td>
                    <td style={{ padding: '1rem' }}>Camiseta Oversize Negra</td>
                    <td style={{ padding: '1rem' }}>500 Unidades</td>
                    <td style={{ padding: '1rem' }}><span style={{ padding: '0.25rem 0.75rem', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 'bold', backgroundColor: 'rgba(59, 130, 246, 0.2)', color: '#3b82f6', border: '1px solid #3b82f6' }}>En Corte</span></td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <button style={{ background: 'none', border: 'none', color: '#f59e0b', cursor: 'pointer', marginRight: '0.75rem' }}><Edit size={16} /></button>
                      <button style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}><Trash2 size={16} /></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* VISTA 4: INGRESO INSUMOS */}
        {moduloActivo === 'insumos' && (
          <div className="module-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <input type="text" placeholder="Buscar Insumo..." style={{ width: '350px', padding: '0.6rem 1rem', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#121212', color: '#fff' }} />
              <button style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', backgroundColor: '#f59e0b', color: '#000', fontWeight: 'bold', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                <PackagePlus size={18} /> Registrar Insumo
              </button>
            </div>
            <div className="table-wrapper">
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #374151', backgroundColor: '#1f2937' }}>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Código</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Insumo</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Stock</th>
                    <th style={{ padding: '1rem', color: '#f59e0b', textAlign: 'center' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #27272a' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>INS-001</td>
                    <td style={{ padding: '1rem' }}>Hilo Poliéster Negro</td>
                    <td style={{ padding: '1rem' }}>120 Conos</td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <button style={{ background: 'none', border: 'none', color: '#f59e0b', cursor: 'pointer', marginRight: '0.75rem' }}><Edit size={16} /></button>
                      <button style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}><Trash2 size={16} /></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* VISTA 5: FICHA TÉCNICA */}
        {moduloActivo === 'ficha' && (
          <div className="module-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <input type="text" placeholder="Buscar Ficha..." style={{ width: '350px', padding: '0.6rem 1rem', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#121212', color: '#fff' }} />
              <button style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', backgroundColor: '#f59e0b', color: '#000', fontWeight: 'bold', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                <FileText size={18} /> Nueva Ficha
              </button>
            </div>
            <div className="table-wrapper">
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #374151', backgroundColor: '#1f2937' }}>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Referencia</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Prenda</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Tela</th>
                    <th style={{ padding: '1rem', color: '#f59e0b', textAlign: 'center' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #27272a' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>REF-001</td>
                    <td style={{ padding: '1rem' }}>Camiseta Oversize</td>
                    <td style={{ padding: '1rem' }}>Algodón 100%</td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <button style={{ background: 'none', border: 'none', color: '#f59e0b', cursor: 'pointer', marginRight: '0.75rem' }}><Edit size={16} /></button>
                      <button style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}><Trash2 size={16} /></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* VISTA 6: CALIDAD */}
        {moduloActivo === 'calidad' && (
          <div className="module-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <input type="text" placeholder="Buscar Auditoría..." style={{ width: '350px', padding: '0.6rem 1rem', borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#121212', color: '#fff' }} />
              <button style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', backgroundColor: '#f59e0b', color: '#000', fontWeight: 'bold', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                <ShieldCheck size={18} /> Nueva Auditoría
              </button>
            </div>
            <div className="table-wrapper">
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #374151', backgroundColor: '#1f2937' }}>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Lote</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Inspector</th>
                    <th style={{ padding: '1rem', color: '#f59e0b' }}>Resultado</th>
                    <th style={{ padding: '1rem', color: '#f59e0b', textAlign: 'center' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #27272a' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>LOTE-08</td>
                    <td style={{ padding: '1rem' }}>Maria Fernanda</td>
                    <td style={{ padding: '1rem' }}><span style={{ padding: '0.25rem 0.75rem', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 'bold', backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#10b981', border: '1px solid #10b981' }}>Aprobado</span></td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <button style={{ background: 'none', border: 'none', color: '#f59e0b', cursor: 'pointer', marginRight: '0.75rem' }}><Edit size={16} /></button>
                      <button style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}><Trash2 size={16} /></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}