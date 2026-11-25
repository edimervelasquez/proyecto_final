import '../styles/Trazabilidad.css';

const fechaLegible = (fecha) => {
  if (!fecha) return 'No registrada';
  const parsed = new Date(fecha);
  return Number.isNaN(parsed.getTime())
    ? fecha
    : parsed.toLocaleString('es-CO');
};

const estadoClase = (estado) => {
  const valor = (estado || '').toLowerCase();
  if (/(aprob|finaliz|complet|exitos|activo|entrada)/.test(valor)) return 'success';
  if (/(inactiv|rechaz|error|elimin)/.test(valor)) return 'danger';
  if (/(retras|pendient|bajo|alert|pausa)/.test(valor)) return 'warning';
  return 'progress';
};

export default function TrazabilidadTable({
  titulo,
  registros,
  cargando,
  error,
  vacio = 'Todavía no hay registros.',
}) {
  return (
    <section className="trazabilidad-card">
      <h3>{titulo}</h3>
      {cargando && <p className="trazabilidad-info">Cargando información...</p>}
      {error && <p className="trazabilidad-error" role="alert">{error}</p>}
      {!cargando && !error && registros.length === 0 && (
        <p className="trazabilidad-info">{vacio}</p>
      )}
      {!cargando && !error && registros.length > 0 && (
        <div className="trazabilidad-scroll">
          <table className="trazabilidad-table">
            <thead>
              <tr>
                <th>Registro</th>
                <th>Detalle</th>
                <th>Ingresado por</th>
                <th>Fecha</th>
                <th>Proceso</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {registros.map((registro) => (
                <tr key={registro.id || registro.id_orden || registro.id_ingreso || registro.sku_prenda || registro.id_control}>
                  <td>{registro.referencia}</td>
                  <td>{registro.detalle}</td>
                  <td>{registro.registrado_por || 'No registrado'}</td>
                  <td>{fechaLegible(registro.fecha_registro)}</td>
                  <td>{registro.proceso || 'Sin registrar'}</td>
                  <td>
                    <span className={`status-badge ${estadoClase(registro.estado)}`}>
                      {registro.estado || 'Sin registrar'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
