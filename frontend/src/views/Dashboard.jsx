import { useState } from 'react';
import { 
  ShieldCheck, 
  Package, 
  Scissors, 
  Layers, 
  CheckCircle, 
  Users, 
  LogOut, 
  User,
  FileText 
} from 'lucide-react';
import IngresoInsumos from './IngresoInsumos';
import Produccion from './Produccion';
import Calidad from './Calidad';
import GestionEmpleados from './GestionEmpleados';
import FichaTecnica from './FichaTecnica';
import '../styles/components/Dashboard.css';

export default function Dashboard({ user, onLogout }) {
  const [moduloActivo, setModuloActivo] = useState('resumen');

  return (
    <div className="dashboard-layout">
      {/* BARRA LATERAL */}
      <aside className="sidebar">
        <div>
          <div className="sidebar-header">
            <ShieldCheck size={32} color="#f59e0b" />
            <h2>SIES Textil</h2>
          </div>

          <nav className="sidebar-nav">
            <button 
              className={`nav-item ${moduloActivo === 'resumen' ? 'active' : ''}`}
              onClick={() => setModuloActivo('resumen')}
            >
              <Layers size={20} />
              Resumen General
            </button>
            <button 
              className={`nav-item ${moduloActivo === 'ficha' ? 'active' : ''}`}
              onClick={() => setModuloActivo('ficha')}
            >
              <FileText size={20} />
              Fichas Técnicas
            </button>
            <button 
              className={`nav-item ${moduloActivo === 'insumos' ? 'active' : ''}`}
              onClick={() => setModuloActivo('insumos')}
            >
              <Package size={20} />
              Insumos
            </button>
            <button 
              className={`nav-item ${moduloActivo === 'produccion' ? 'active' : ''}`}
              onClick={() => setModuloActivo('produccion')}
            >
              <Scissors size={20} />
              Producción
            </button>
            <button 
              className={`nav-item ${moduloActivo === 'calidad' ? 'active' : ''}`}
              onClick={() => setModuloActivo('calidad')}
            >
              <CheckCircle size={20} />
              Calidad
            </button>
            <button 
              className={`nav-item ${moduloActivo === 'personal' ? 'active' : ''}`}
              onClick={() => setModuloActivo('personal')}
            >
              <Users size={20} />
              Personal
            </button>
          </nav>
        </div>

        <button onClick={onLogout} className="btn-logout">
          <LogOut size={18} />
          Cerrar Sesión
        </button>
      </aside>

      {/* ÁREA DE TRABAJO */}
      <main className="main-content">
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
            <span>{user?.empleado || user?.correo_usuario || 'Operador'}</span>
          </div>
        </header>

        <section className="content-body">
          {moduloActivo === 'resumen' && (
            <>
              {/* MÉTRICAS PRINCIPALES */}
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-icon"><Package size={24} /></div>
                  <div className="metric-info">
                    <h3>Total Insumos</h3>
                    <p>128 items</p>
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon"><Scissors size={24} /></div>
                  <div className="metric-info">
                    <h3>Órdenes Activas</h3>
                    <p>14 Lotes</p>
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon"><CheckCircle size={24} /></div>
                  <div className="metric-info">
                    <h3>Aprobación Calidad</h3>
                    <p>98.5%</p>
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon"><Users size={24} /></div>
                  <div className="metric-info">
                    <h3>Operarios en Taller</h3>
                    <p>22 Activos</p>
                  </div>
                </div>
              </div>

              <div className="module-placeholder">
                <p>Selecciona un módulo en el menú lateral para gestionar la información.</p>
              </div>
            </>
          )}

          {moduloActivo === 'ficha' && <FichaTecnica />}

          {moduloActivo === 'insumos' && <IngresoInsumos />}

          {moduloActivo === 'produccion' && <Produccion />}

          {moduloActivo === 'calidad' && <Calidad />}

          {moduloActivo === 'personal' && <GestionEmpleados />}
        </section>
      </main>
    </div>
  );
}