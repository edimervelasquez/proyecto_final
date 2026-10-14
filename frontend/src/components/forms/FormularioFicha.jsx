import '../../styles/FichaTecnica.css';

const FormularioFicha = ({
  formData,
  catalogo,
  onChange,
  onInsumoChange,
  onAddInsumo,
  onRemoveInsumo,
  onSubmit,
  cargando,
}) => (
  <div className="form-card">
    <div className="form-card-header">
      <h3>Crear Ficha Técnica</h3>
      <p>Define los materiales y cantidades requeridos para fabricar un producto.</p>
    </div>

    <form onSubmit={onSubmit} className="form-grid-layout">
      <div className="grid-2">
        <div className="input-group">
          <label>SKU / Referencia del producto *</label>
          <input
            type="text"
            name="sku_prenda"
            placeholder="Ej. CAM-OV-NEG-M"
            value={formData.sku_prenda}
            onChange={onChange}
            maxLength="50"
            required
          />
        </div>
        <div className="input-group">
          <label>Nombre del producto *</label>
          <input
            type="text"
            name="nombre_producto"
            placeholder="Ej. Camiseta Oversize Negra"
            value={formData.nombre_producto}
            onChange={onChange}
            required
          />
        </div>
      </div>

      <div className="input-group">
        <label>Descripción / Observaciones</label>
        <input
          type="text"
          name="descripcion"
          value={formData.descripcion}
          onChange={onChange}
        />
      </div>

      <div className="grid-2">
        <div className="input-group">
          <label>Costo de mano de obra por prenda ($) *</label>
          <input
            type="number"
            name="costo_mano_obra"
            min="0"
            step="0.01"
            value={formData.costo_mano_obra}
            onChange={onChange}
            required
          />
        </div>
        <div className="input-group">
          <label>Precio mayorista por prenda ($) *</label>
          <input
            type="number"
            name="precio_mayorista"
            min="0.01"
            step="0.01"
            value={formData.precio_mayorista}
            onChange={onChange}
            required
          />
        </div>
      </div>

      <div className="input-group">
        <label>Precio al detal por prenda ($) *</label>
        <input
          type="number"
          name="precio_detal"
          min="0.01"
          step="0.01"
          value={formData.precio_detal}
          onChange={onChange}
          required
        />
      </div>

      <h4>Insumos por unidad</h4>
      {formData.insumos.map((insumo, index) => (
        <div className="grid-2" key={`insumo-${index}`}>
          <div className="input-group">
            <label>Materia prima *</label>
            <select
              value={insumo.id_materiaPrima}
              onChange={(event) => onInsumoChange(index, 'id_materiaPrima', event.target.value)}
              required
            >
              <option value="">Selecciona un insumo</option>
              {catalogo.map((material) => (
                <option key={material.id_materiaPrima} value={material.id_materiaPrima}>
                  {material.nombre_material}
                </option>
              ))}
            </select>
          </div>
          <div className="input-group">
            <label>Cantidad requerida por unidad *</label>
            <div className="grid-2">
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={insumo.cantidad_estimada}
                onChange={(event) => onInsumoChange(index, 'cantidad_estimada', event.target.value)}
                required
              />
              {formData.insumos.length > 1 && (
                <button type="button" className="btn-sies-primary" onClick={() => onRemoveInsumo(index)}>
                  Quitar
                </button>
              )}
            </div>
          </div>
        </div>
      ))}

      <button type="button" className="btn-sies-primary" onClick={onAddInsumo}>
        Agregar otro insumo
      </button>

      <div className="form-actions-right">
        <button type="submit" className="btn-sies-primary" disabled={cargando || catalogo.length === 0}>
          {cargando ? 'Guardando...' : 'Crear Ficha Técnica'}
        </button>
      </div>
    </form>
  </div>
);

export default FormularioFicha;
