import React from 'react';
import '../styles/Produccion.css';

const FormularioProduccion = ({ formData, onChange, onSubmit, cargando }) => {
  return (
    <div className="form-card">
      <div className="form-card-header">
        <h3>Nueva Orden de Producción</h3>
        <p>Registra una nueva orden de trabajo vinculada a una ficha técnica.</p>
      </div>

      <form onSubmit={onSubmit} className="form-grid-layout">
        <div className="grid-2">
          <div className="input-group">
            <label>ID Ficha Técnica / Producto *</label>
            <input
              type="number"
              name="id_ficha_tecnica"
              placeholder="Ej. 1"
              value={formData.id_ficha_tecnica}
              onChange={onChange}
              required
            />
          </div>

          <div className="input-group">
            <label>Cantidad a Producir *</label>
            <input
              type="number"
              name="cantidad_producir"
              placeholder="Ej. 100"
              value={formData.cantidad_producir}
              onChange={onChange}
              required
            />
          </div>
        </div>

        <div className="grid-2">
          <div className="input-group">
            <label>Fecha de Inicio</label>
            <input
              type="date"
              name="fecha_inicio"
              value={formData.fecha_inicio}
              onChange={onChange}
            />
          </div>

          <div className="input-group">
            <label>Lote / Orden de Producción</label>
            <input
              type="text"
              name="lote"
              placeholder="Ej. LOTE-2026-001"
              value={formData.lote}
              onChange={onChange}
            />
          </div>
        </div>

        <div className="form-actions-right">
          <button type="submit" className="btn-sies-primary" disabled={cargando}>
            {cargando ? 'Iniciando Orden...' : 'Iniciar Producción'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormularioProduccion;