import FormularioProduccion from '../../components/forms/FormularioProduccion';
import TrazabilidadTable from '../../components/TrazabilidadTable';
import useProduccion, { MOTIVOS_RETRASO } from '../../hooks/useProduccion';
import '../../styles/Produccion.css';
import '../../styles/Retrasos.css';

const Produccion = ({ user }) => {
  const {
    formData,
    fichas,
    areas,
    ordenes,
    retrasos,
    ordenRetraso,
    setOrdenRetraso,
    motivoRetraso,
    setMotivoRetraso,
    detalleRetraso,
    setDetalleRetraso,
    mensaje,
    cargando,
    cargandoLista,
    errorLista,
    puedeReportarRetraso,
    filas,
    handleSubmit,
    iniciarRetraso,
    reanudarOrden,
    avanzarOrden,
    manejarCambioFormulario,
    duracion,
  } = useProduccion(user);

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Control de Producción</h2>
        <span className="badge-modulo">Órdenes de Trabajo</span>
      </div>

      {mensaje.texto && (
        <div className={`alerta-sies ${mensaje.tipo}`} role={mensaje.tipo === 'error' ? 'alert' : 'status'}>
          {mensaje.texto}
        </div>
      )}

      <FormularioProduccion
        formData={formData}
        fichas={fichas}
        areas={areas}
        onChange={manejarCambioFormulario}
        onSubmit={handleSubmit}
        cargando={cargando || cargandoLista}
      />

      <TrazabilidadTable
        titulo="Órdenes de producción"
        registros={filas}
        cargando={cargandoLista}
        error={errorLista}
        vacio="Aún no se han registrado órdenes de producción."
      />

      <section className="retrasos-panel">
        <h3>Retrasos de producción</h3>
        <p>La orden conserva su área actual mientras está detenida.</p>
        <div className="retrasos-lista">
          {ordenes.map((orden) => {
            const retrasoAbierto = retrasos.find(
              (retraso) => retraso.id_orden === orden.id_orden && retraso.abierto,
            );
            return (
              <article className="retraso-orden" key={orden.id_orden}>
                <div>
                  <strong>OP-{orden.id_orden} · {orden.sku_prenda}</strong>
                  <span>{orden.area} · {orden.estado}</span>
                  {retrasoAbierto && (
                    <div className="retraso-alerta" role="status">
                      Retraso activo: {retrasoAbierto.motivo}
                      {retrasoAbierto.detalle ? ` — ${retrasoAbierto.detalle}` : ''}
                      {' · '}Inició {new Date(retrasoAbierto.fecha_inicio).toLocaleString('es-CO')}
                      {' · '}{duracion(retrasoAbierto.segundos_detenida)}
                    </div>
                  )}
                  {orden.siguiente_etapa && !retrasoAbierto && (user?.id_rol === 1 || user?.id_rol === 2) && (
                    <button
                      type="button"
                      className="retraso-button"
                      disabled={cargando || cargandoLista}
                      onClick={() => avanzarOrden(orden)}
                    >
                      Avanzar a {orden.siguiente_etapa}
                    </button>
                  )}
                </div>
                {retrasoAbierto && puedeReportarRetraso ? (
                  <button
                    type="button"
                    className="retraso-button"
                    onClick={() => reanudarOrden(retrasoAbierto.id_retraso)}
                    disabled={cargando}
                  >
                    Continuar producción
                  </button>
                ) : !retrasoAbierto && puedeReportarRetraso && orden.estado !== 'Finalizada' && (
                  <button
                    type="button"
                    className="retraso-button"
                    onClick={() => {
                      setOrdenRetraso(String(orden.id_orden));
                      setDetalleRetraso('');
                    }}
                    disabled={cargando || cargandoLista}
                  >
                    Registrar retraso
                  </button>
                )}
              </article>
            );
          })}
          {!cargandoLista && ordenes.length === 0 && (
            <p>No hay órdenes a las que registrar retrasos.</p>
          )}
        </div>

        {ordenRetraso && (
          <form className="retraso-form" onSubmit={iniciarRetraso}>
            <h4>Registrar retraso · OP-{ordenRetraso}</h4>
            <label htmlFor="motivo-retraso">Motivo *</label>
            <select
              id="motivo-retraso"
              value={motivoRetraso}
              onChange={(event) => setMotivoRetraso(event.target.value)}
              required
            >
              {MOTIVOS_RETRASO.map((motivo) => (
                <option key={motivo} value={motivo}>{motivo}</option>
              ))}
            </select>
            <label htmlFor="detalle-retraso">
              {motivoRetraso === 'Otro' ? 'Explica el motivo *' : 'Detalle (opcional)'}
            </label>
            <textarea
              id="detalle-retraso"
              value={detalleRetraso}
              onChange={(event) => setDetalleRetraso(event.target.value)}
              maxLength="1000"
              required={motivoRetraso === 'Otro'}
              rows="3"
            />
            <div className="retraso-form-acciones">
              <button type="submit" className="retraso-button" disabled={cargando}>
                {cargando ? 'Guardando...' : 'Iniciar retraso'}
              </button>
              <button
                type="button"
                className="retraso-button secundario"
                onClick={() => setOrdenRetraso('')}
                disabled={cargando}
              >
                Cancelar
              </button>
            </div>
          </form>
        )}

        <h4>Historial de retrasos</h4>
        <div className="retrasos-lista">
          {retrasos.map((retraso) => (
            <div className="retraso-historico" key={retraso.id_retraso}>
              <strong>OP-{retraso.id_orden} · {retraso.area} · {retraso.motivo}</strong>
              <span>
                {retraso.detalle ? `${retraso.detalle} · ` : ''}
                Registró {retraso.registrado_por} ·{' '}
                {new Date(retraso.fecha_inicio).toLocaleString('es-CO')} ·{' '}
                {retraso.abierto
                  ? 'En curso'
                  : `${duracion(retraso.segundos_detenida)} · Reanudó ${retraso.reanudado_por || 'No registrado'} el ${new Date(retraso.fecha_fin).toLocaleString('es-CO')}`}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Produccion;
