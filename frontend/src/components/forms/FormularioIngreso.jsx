import '../../styles/IngresoInsumos.css';

const FormularioIngreso = ({
  formData,
  catalogo,
  onChange,
  onSubmit,
  cargando,
}) => {
  return (
    <div className="form-card">
      <div className="form-card-header">
        <h3>Registrar Entrada de Materiales</h3>
        <p>Ingresa los detalles del insumo recibido para actualizar el inventario.</p>
      </div>

      <form onSubmit={onSubmit} className="form-grid-layout">
        <div className="grid-2">
          <div className="input-group">
            <label>Materia prima / insumo *</label>
            <select
              name="id_materia_prima"
              value={formData.id_materia_prima}
              onChange={onChange}
              required
            >
              <option value="">Selecciona un insumo</option>
              <option value="nuevo">Registrar un nuevo insumo</option>
              {catalogo.map((material) => (
                <option key={material.id_materiaPrima} value={material.id_materiaPrima}>
                  {material.nombre_material} (stock: {material.stock})
                </option>
              ))}
            </select>
          </div>

          <div className="input-group">
            <label>Cantidad Ingresada *</label>
            <input
              type="number"
              step="1"
              min="1"
              name="cantidad_ingresada"
              placeholder="Ej. 150.00"
              value={formData.cantidad_ingresada}
              onChange={onChange}
              required
            />
          </div>
        </div>

        {formData.id_materia_prima === 'nuevo' && (
          <div className="grid-2">
            <div className="input-group">
              <label>Nombre del nuevo insumo *</label>
              <input
                type="text"
                name="nombre_material"
                maxLength="100"
                value={formData.nombre_material}
                onChange={onChange}
                required
              />
            </div>
            <div className="input-group">
              <label>Stock mínimo para alertas</label>
              <input
                type="number"
                min="0"
                step="1"
                name="stock_minimo"
                value={formData.stock_minimo}
                onChange={onChange}
              />
            </div>
          </div>
        )}

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

        <div className="input-group">
          <label>Fecha del ingreso</label>
          <input
            type="date"
            name="fecha_ingreso"
            value={formData.fecha_ingreso}
            onChange={onChange}
          />
        </div>

        <div className="form-actions-right">
          <button
            type="submit"
            className="btn-sies-primary"
            disabled={cargando || !formData.id_materia_prima}
          >
            {cargando ? 'Procesando Entrada...' : 'Guardar y Registrar Insumo'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormularioIngreso;