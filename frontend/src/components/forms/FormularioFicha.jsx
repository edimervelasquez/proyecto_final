import '../../styles/FichaTecnica.css';

const FormularioFicha = ({ formData, onChange, onSubmit, cargando }) => {
  return (
    <div className="form-card">
      <div className="form-card-header">
        <h3>Crear Ficha Técnica</h3>
        <p>Define las especificaciones de materia prima para la elaboración del producto.</p>
      </div>

      <form onSubmit={onSubmit} className="form-grid-layout">
        <div className="grid-2">
          <div className="input-group">
            <label>Nombre del Producto / Referencia *</label>
            <input
              type="text"
              name="nombre_producto"
              placeholder="Ej. Camiseta Over Size Talla M"
              value={formData.nombre_producto}
              onChange={onChange}
              required
            />
          </div>

          <div className="input-group">
            <label>ID Materia Prima Requerida *</label>
            <input
              type="number"
              name="id_materia_prima"
              placeholder="Ej. 1"
              value={formData.id_materia_prima}
              onChange={onChange}
              required
            />
          </div>
        </div>

        <div className="grid-2">
          <div className="input-group">
            <label>Cantidad Requerida por Unidad *</label>
            <input
              type="number"
              step="0.01"
              name="cantidad_requerida"
              placeholder="Ej. 1.5"
              value={formData.cantidad_requerida}
              onChange={onChange}
              required
            />
          </div>

          <div className="input-group">
            <label>Descripción / Observaciones</label>
            <input
              type="text"
              name="descripcion"
              placeholder="Ej. Tela 100% algodón"
              value={formData.descripcion}
              onChange={onChange}
            />
          </div>
        </div>

        <div className="form-actions-right">
          <button type="submit" className="btn-sies-primary" disabled={cargando}>
            {cargando ? 'Guardando...' : 'Crear Ficha Técnica'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormularioFicha;