import React from 'react';
import '../styles/IngresoInsumos.css';

const FormularioIngreso = ({ formData, onChange, onSubmit, cargando }) => {
  return (
    <div className="form-card">
      <div className="form-card-header">
        <h3>Registrar Entrada de Materiales</h3>
        <p>Ingresa los detalles del insumo recibido para actualizar el inventario.</p>
      </div>

      <form onSubmit={onSubmit} className="form-grid-layout">
        <div className="grid-2">
          <div className="input-group">
            <label>ID Materia Prima / Insumo *</label>
            <input
              type="number"
              name="id_materia_prima"
              placeholder="Ej. 102"
              value={formData.id_materia_prima}
              onChange={onChange}
              required
            />
          </div>

          <div className="input-group">
            <label>Cantidad Ingresada *</label>
            <input
              type="number"
              step="0.01"
              name="cantidad_ingresada"
              placeholder="Ej. 150.00"
              value={formData.cantidad_ingresada}
              onChange={onChange}
              required
            />
          </div>
        </div>

        <div className="grid-2">
          <div className="input-group">
            <label>Proveedor *</label>
            <input
              type="text"
              name="proveedor"
              placeholder="Ej. Textiles Colombia S.A."
              value={formData.proveedor}
              onChange={onChange}
              required
            />
          </div>

          <div className="input-group">
            <label>Costo Unitario ($)</label>
            <input
              type="number"
              step="0.01"
              name="costo_unitario"
              placeholder="Ej. 25000"
              value={formData.costo_unitario}
              onChange={onChange}
            />
          </div>
        </div>

        <div className="form-actions-right">
          <button type="submit" className="btn-sies-primary" disabled={cargando}>
            {cargando ? 'Procesando Entrada...' : 'Guardar y Registrar Insumo'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormularioIngreso;