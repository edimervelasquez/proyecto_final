import FormularioIngreso from '../../components/forms/FormularioIngreso';
import TrazabilidadTable from '../../components/TrazabilidadTable';
import useIngresoInsumos from '../../hooks/useIngresoInsumos';
import '../../styles/IngresoInsumos.css';

const IngresoInsumos = ({ user }) => {
  const {
    formData,
    catalogo,
    minimos,
    mensaje,
    cargando,
    cargandoLista,
    errorLista,
    esAdministrador,
    filas,
    filasMovimientos,
    handleChange,
    handleSubmit,
    guardarMinimo,
    cambiarMinimo,
  } = useIngresoInsumos(user);

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Gestión e Ingreso de Insumos</h2>
        <span className="badge-modulo">Inventario / Materia Prima</span>
      </div>

      {mensaje.texto && (
        <div className={`alerta-sies ${mensaje.tipo}`} role={mensaje.tipo === 'error' ? 'alert' : 'status'}>
          {mensaje.texto}
        </div>
      )}

      <FormularioIngreso
        formData={formData}
        catalogo={catalogo}
        onChange={handleChange}
        onSubmit={handleSubmit}
        cargando={cargando}
      />

      <section className="form-card stock-alerts">
        <div className="form-card-header">
          <h3>Alertas de stock bajo</h3>
          <p>Se muestran los insumos cuyo stock disponible es igual o inferior al mínimo configurado.</p>
        </div>
        {catalogo.filter((material) => material.alerta_bajo_stock).length === 0
          ? <p className="trazabilidad-info">No hay insumos por debajo del mínimo.</p>
          : (
            <ul className="stock-alert-list">
              {catalogo.filter((material) => material.alerta_bajo_stock).map((material) => (
                <li key={material.id_materiaPrima}>
                  <strong>{material.nombre_material}</strong>
                  <span>Disponible: {material.stock} · Mínimo: {material.stock_minimo}</span>
                </li>
              ))}
            </ul>
          )}
      </section>

      {esAdministrador && (
        <section className="form-card stock-minimums">
          <div className="form-card-header">
            <h3>Configurar mínimos por insumo</h3>
            <p>Solo administradores pueden editar los niveles que disparan las alertas.</p>
          </div>
          <div className="stock-minimum-list">
            {catalogo.map((material) => (
              <form
                className="stock-minimum-row"
                key={material.id_materiaPrima}
                onSubmit={(event) => {
                  event.preventDefault();
                  guardarMinimo(material);
                }}
              >
                <strong>{material.nombre_material}</strong>
                <span>Disponible: {material.stock}</span>
                <label>
                  Mínimo
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={minimos[material.id_materiaPrima] ?? '0'}
                    onChange={(event) => cambiarMinimo(
                      material.id_materiaPrima,
                      event.target.value,
                    )}
                  />
                </label>
                <button type="submit" className="btn-sies-secondary">
                  Guardar
                </button>
              </form>
            ))}
          </div>
        </section>
      )}

      <TrazabilidadTable
        titulo="Ingresos de insumos registrados"
        registros={filas}
        cargando={cargandoLista}
        error={errorLista}
        vacio="Aún no se han registrado ingresos de insumos."
      />
      <TrazabilidadTable
        titulo="Historial auditable de movimientos"
        registros={filasMovimientos}
        cargando={cargandoLista}
        error={errorLista}
        vacio="Aún no se han registrado movimientos."
      />
    </div>
  );
};

export default IngresoInsumos;
