import '../../styles/Produccion.css';

const FormularioProduccion = ({
  formData,
  fichas,
  areas,
  onChange,
  onSubmit,
  cargando,
}) => (
  <div className="form-card">
    <div className="form-card-header">
      <h3>Nueva Orden de Producción</h3>
      <p>Registra una orden vinculada a una ficha técnica existente.</p>
    </div>

    <form onSubmit={onSubmit} className="form-grid-layout">
      <div className="grid-2">
        <div className="input-group">
          <label>Ficha técnica / producto *</label>
          <select name="sku_prenda" value={formData.sku_prenda} onChange={onChange} required>
            <option value="">Selecciona una ficha</option>
            {fichas.map((ficha) => (
              <option key={ficha.sku_prenda} value={ficha.sku_prenda}>
                {ficha.nombre_producto} ({ficha.sku_prenda})
              </option>
            ))}
          </select>
        </div>
        <div className="input-group">
          <label>Área de producción *</label>
          <select name="id_area" value={formData.id_area} onChange={onChange} required>
            <option value="">Selecciona un área</option>
            {areas.map((area) => (
              area.nombre_area === 'Corte' && (
              <option key={area.id_area} value={area.id_area}>
                {area.nombre_area || `Área ${area.id_area}`}
              </option>
              )
            ))}
          </select>
        </div>
      </div>

      <div className="grid-2">
        <div className="input-group">
          <label>Cantidad a producir *</label>
          <input
            type="number"
            name="cantidad_a_producir"
            min="1"
            step="1"
            value={formData.cantidad_a_producir}
            onChange={onChange}
            required
          />
        </div>
        <div className="input-group">
          <label>Fecha estimada de entrega *</label>
          <input
            type="date"
            name="fecha_entrega"
            value={formData.fecha_entrega}
            onChange={onChange}
            required
          />
        </div>
        <div className="input-group">
          <label>Destino de producción *</label>
          <select
            name="canal_destino"
            value={formData.canal_destino}
            onChange={onChange}
            required
          >
            <option value="DETAL">Venta al detal · Bodega del local</option>
            <option value="MAYORISTA">Venta mayorista · Bodega mayorista</option>
          </select>
        </div>
      </div>

      <div className="form-actions-right">
        <button
          type="submit"
          className="btn-sies-primary"
          disabled={cargando || !fichas.length || !formData.id_area}
        >
          {cargando ? 'Iniciando orden...' : 'Crear orden de producción'}
        </button>
      </div>
      {!fichas.length && (
        <p role="status">
          Primero crea una ficha técnica.
        </p>
      )}
    </form>
  </div>
);

export default FormularioProduccion;
