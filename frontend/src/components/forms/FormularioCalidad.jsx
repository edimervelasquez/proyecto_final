import '../../styles/Calidad.css';

const FormularioCalidad = ({ formData, onChange, onSubmit, cargando }) => {
  return (
    <div className="form-card">
      <div className="form-card-header">
        <h3>Inspección y Control de Calidad</h3>
        <p>Registra el balance de piezas aprobadas y defectuosas por orden.</p>
      </div>

      <form onSubmit={onSubmit} className="form-grid-layout">
        <div className="grid-2">
          <div className="input-group">
            <label>ID Orden de Producción *</label>
            <input
              type="number"
              name="id_produccion"
              placeholder="Ej. 1"
              value={formData.id_produccion}
              onChange={onChange}
              required
            />
          </div>

          <div className="input-group">
            <label>Piezas Aprobadas *</label>
            <input
              type="number"
              name="piezas_aprobadas"
              placeholder="Ej. 95"
              value={formData.piezas_aprobadas}
              onChange={onChange}
              required
            />
          </div>
        </div>

        <div className="grid-2">
          <div className="input-group">
            <label>Piezas Defectuosas / Rechazadas *</label>
            <input
              type="number"
              name="piezas_defectuosas"
              placeholder="Ej. 5"
              value={formData.piezas_defectuosas}
              onChange={onChange}
              required
            />
          </div>

          <div className="input-group">
            <label>Observaciones de Inspección</label>
            <input
              type="text"
              name="observaciones"
              placeholder="Ej. Costura defectuosa"
              value={formData.observaciones}
              onChange={onChange}
            />
          </div>
        </div>

        <div className="form-actions-right">
          <button type="submit" className="btn-sies-primary" disabled={cargando}>
            {cargando ? 'Registrando...' : 'Registrar Inspección'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormularioCalidad;