import { useCallback, useEffect, useState } from 'react';
import FormularioProduccion from '../../components/forms/FormularioProduccion';
import TrazabilidadTable from '../../components/TrazabilidadTable';
import { insumoService } from '../../services/insumoService';
import { produccionService } from '../../services/produccionService';
import '../../styles/Produccion.css';
import '../../styles/Retrasos.css';

const MOTIVOS_RETRASO = [
  'Reparación de prendas con defecto',
  'Falta de materia prima',
  'Falla de maquinaria',
  'Espera de instrucciones o aprobación',
  'Otro',
];

const formularioVacio = {
  sku_prenda: '',
  id_area: '',
  cantidad_a_producir: '',
  fecha_entrega: '',
  canal_destino: 'DETAL',
};

const Produccion = ({ user }) => {
  const [formData, setFormData] = useState(formularioVacio);
  const [fichas, setFichas] = useState([]);
  const [areas, setAreas] = useState([]);
  const [ordenes, setOrdenes] = useState([]);
  const [retrasos, setRetrasos] = useState([]);
  const [ordenRetraso, setOrdenRetraso] = useState('');
  const [motivoRetraso, setMotivoRetraso] = useState(MOTIVOS_RETRASO[0]);
  const [detalleRetraso, setDetalleRetraso] = useState('');
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);
  const [cargandoLista, setCargandoLista] = useState(true);
  const [errorLista, setErrorLista] = useState('');
  const puedeReportarRetraso = user?.id_rol === 1 || user?.id_rol === 2;

  const cargarDatos = useCallback(() => (
    Promise.all([
        insumoService.obtenerFichas(),
        produccionService.obtenerAreas(),
        produccionService.obtenerOrdenes(),
        produccionService.obtenerRetrasos(),
      ]).then(([fichasTecnicas, areasProduccion, registros, listaRetrasos]) => ({
        fichasTecnicas,
        areasProduccion,
        registros,
        listaRetrasos,
      }))
  ), []);

  useEffect(() => {
    cargarDatos()
      .then(({ fichasTecnicas, areasProduccion, registros, listaRetrasos }) => {
        setFichas(fichasTecnicas);
        setAreas(areasProduccion);
        setOrdenes(registros);
        setRetrasos(listaRetrasos);
        const corte = areasProduccion.find((area) => area.nombre_area === 'Corte');
        if (corte) {
          setFormData((actual) => (
            actual.id_area ? actual : { ...actual, id_area: String(corte.id_area) }
          ));
        }
        setErrorLista('');
        setCargandoLista(false);
      })
      .catch((error) => {
        setErrorLista(error.message || 'No se pudieron cargar las órdenes de producción.');
        setCargandoLista(false);
      });
  }, [cargarDatos]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await produccionService.registrarOrden({
        sku_prenda: formData.sku_prenda,
        id_area: Number(formData.id_area),
        cantidad_a_producir: Number(formData.cantidad_a_producir),
        fecha_entrega: formData.fecha_entrega,
        canal_destino: formData.canal_destino,
      });
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      setFormData(formularioVacio);
      setCargandoLista(true);
      const { fichasTecnicas, areasProduccion, registros, listaRetrasos } = await cargarDatos();
      setFichas(fichasTecnicas);
      setAreas(areasProduccion);
      setOrdenes(registros);
      setRetrasos(listaRetrasos);
      setErrorLista('');
      setCargandoLista(false);
    } catch (error) {
      setMensaje({
        texto: error.message || 'No se pudo registrar la orden.',
        tipo: 'error',
      });
    } finally {
      setCargando(false);
    }
  };

  const iniciarRetraso = async (event) => {
    event.preventDefault();
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await produccionService.registrarRetraso(
        Number(ordenRetraso),
        {
          motivo: motivoRetraso,
          detalle: detalleRetraso.trim() || null,
        },
      );
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      setOrdenRetraso('');
      setMotivoRetraso(MOTIVOS_RETRASO[0]);
      setDetalleRetraso('');
      const { fichasTecnicas, areasProduccion, registros, listaRetrasos } = await cargarDatos();
      setFichas(fichasTecnicas);
      setAreas(areasProduccion);
      setOrdenes(registros);
      setRetrasos(listaRetrasos);
      setErrorLista('');
      setCargandoLista(false);
    } catch (error) {
      setMensaje({ texto: error.message || 'No se pudo registrar el retraso.', tipo: 'error' });
    } finally {
      setCargando(false);
    }
  };

  const reanudarOrden = async (idRetraso) => {
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await produccionService.reanudarProduccion(idRetraso);
      const duracion = respuesta.minutos_detenida;
      const tiempo = duracion >= 60
        ? `${Math.floor(duracion / 60)} h ${duracion % 60} min`
        : `${duracion} min`;
      setMensaje({
        texto: `${respuesta.mensaje} Tiempo detenido: ${tiempo}.`,
        tipo: 'exito',
      });
      const { fichasTecnicas, areasProduccion, registros, listaRetrasos } = await cargarDatos();
      setFichas(fichasTecnicas);
      setAreas(areasProduccion);
      setOrdenes(registros);
      setRetrasos(listaRetrasos);
      setErrorLista('');
      setCargandoLista(false);
    } catch (error) {
      setMensaje({ texto: error.message || 'No se pudo reanudar la orden.', tipo: 'error' });
    } finally {
      setCargando(false);
    }
  };

  const avanzarOrden = async (orden) => {
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await produccionService.avanzarEtapa(
        orden.id_orden,
        orden.id_area_siguiente,
      );
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      const { fichasTecnicas, areasProduccion, registros, listaRetrasos } = await cargarDatos();
      setFichas(fichasTecnicas);
      setAreas(areasProduccion);
      setOrdenes(registros);
      setRetrasos(listaRetrasos);
      setErrorLista('');
      setCargandoLista(false);
    } catch (error) {
      setMensaje({ texto: error.message || 'No se pudo avanzar la etapa.', tipo: 'error' });
    } finally {
      setCargando(false);
    }
  };

  const duracion = (segundos) => {
    const minutos = Math.floor(segundos / 60);
    if (minutos < 60) return `${minutos} min`;
    return `${Math.floor(minutos / 60)} h ${minutos % 60} min`;
  };

  const filas = ordenes.map((orden) => ({
    ...orden,
    referencia: `OP-${orden.id_orden}`,
    detalle: `${orden.sku_prenda} · ${orden.cantidad} unidades · ${orden.area}`,
  }));

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
        onChange={(event) => setFormData({
          ...formData,
          [event.target.name]: event.target.value,
        })}
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
