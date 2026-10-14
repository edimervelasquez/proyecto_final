import '../../styles/Calidad.css';

const FormularioCalidad = ({
  formData,
  ordenes,
  ordenesEnProceso,
  onChange,
  onSubmit,
  cargando,
}) => {
  return (
    <div className="form-card">
      <div className="form-card-header">
        <h3>Inspección y Control de Calidad</h3>
        <p>Registra el balance de piezas aprobadas y defectuosas por orden.</p>
      </div>

      <form onSubmit={onSubmit} className="form-grid-layout">
        <div className="grid-2">
          <div className="input-group">
            <label>Orden de producción *</label>
            <select
              name="id_produccion"
              value={formData.id_produccion}
              onChange={onChange}
              required
            >
              <option value="">Selecciona una orden</option>
              {ordenes.map((orden) => (
                <option key={orden.id_orden} value={orden.id_orden}>
                  OP-{orden.id_orden} · {orden.sku_prenda} · {orden.cantidad_entregada}/{orden.cantidad} entregadas
                </option>
              ))}
            </select>
          </div>

          <div className="input-group">
            <label>Piezas Aprobadas *</label>
            <input
              type="number"
              name="cantidad_optima"
              placeholder="Ej. 95"
              min="0"
              step="1"
              value={formData.cantidad_optima}
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
              name="cantidad_defectuosa"
              placeholder="Ej. 5"
              min="0"
              step="1"
              value={formData.cantidad_defectuosa}
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
          <button type="submit" className="btn-sies-primary" disabled={cargando || !ordenes.length}>
            {cargando ? 'Registrando...' : 'Registrar Inspección'}
          </button>
        </div>
        {!ordenes.length && (
          <div className="calidad-ayuda-etapa" role="status">
            <strong>No hay órdenes listas para inspección.</strong>
            <p>
              La orden aparece aquí cuando llegue a <strong>Calidad y Empaque</strong>.
              En Producción, avanza cada orden por Confección y Estampado hasta esa etapa.
            </p>
            {ordenesEnProceso.length > 0 && (
              <ul>
                {ordenesEnProceso.map((orden) => (
                  <li key={orden.id_orden}>
                    <strong>OP-{orden.id_orden}</strong> · {orden.sku_prenda} está en {orden.area}
                    {orden.siguiente_etapa
                      ? `; el siguiente paso es avanzar a ${orden.siguiente_etapa}.`
                      : '.'}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </form>
    </div>
  );
};

export default FormularioCalidad;