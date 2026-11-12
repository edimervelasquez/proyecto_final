import { useCallback, useEffect, useState } from 'react';
import { mermaService } from '../../services/mermaService';
import { produccionService } from '../../services/produccionService';
import '../../styles/Mermas.css';

const formularioVacio = {
  id_produccion: '',
  id_tipo_merma: '',
  cantidad_sobrante: '',
};

const fechaLegible = (fecha) => {
  if (!fecha) return 'No registrada';
  const parsed = new Date(fecha);
  return Number.isNaN(parsed.getTime())
    ? fecha
    : parsed.toLocaleString('es-CO');
};

export default function Mermas() {
  const [formData, setFormData] = useState(formularioVacio);
  const [ordenes, setOrdenes] = useState([]);
  const [tipos, setTipos] = useState([]);
  const [mermas, setMermas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [errorLista, setErrorLista] = useState('');
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const ordenesActivas = ordenes.filter(
    (orden) => orden.estado?.trim().toLocaleLowerCase('es-CO') !== 'finalizada',
  );

  const cargarDatos = useCallback(async () => {
    return Promise.all([
      produccionService.obtenerOrdenes(),
      mermaService.obtenerTipos(),
      mermaService.obtenerMermas(),
    ]);
  }, []);

  useEffect(() => {
    cargarDatos()
      .then(([listaOrdenes, listaTipos, listaMermas]) => {
        setOrdenes(listaOrdenes);
        setTipos(listaTipos);
        setMermas(listaMermas);
        setErrorLista('');
      })
      .catch((error) => {
        setErrorLista(error.message || 'No se pudieron cargar las mermas.');
      })
      .finally(() => setCargando(false));
  }, [cargarDatos]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setEnviando(true);
    setMensaje({ texto: '', tipo: '' });
    try {
      const resultado = await mermaService.registrarMerma({
        id_produccion: Number(formData.id_produccion),
        id_tipo_merma: Number(formData.id_tipo_merma),
        cantidad_sobrante: formData.cantidad_sobrante,
      });
      setMensaje({
        texto: `Merma #${resultado.id_merma} registrada correctamente.`,
        tipo: 'exito',
      });
      setFormData(formularioVacio);
      setCargando(true);
    } catch (error) {
      setMensaje({
        texto: error.message || 'No se pudo registrar la merma.',
        tipo: 'error',
      });
      setCargando(false);
      setEnviando(false);
      return;
    }

    try {
      const [listaOrdenes, listaTipos, listaMermas] = await cargarDatos();
      setOrdenes(listaOrdenes);
      setTipos(listaTipos);
      setMermas(listaMermas);
      setErrorLista('');
    } catch (error) {
      setErrorLista(
        error.message || 'La merma se guardó, pero no se pudo actualizar la lista.',
      );
    } finally {
      setCargando(false);
      setEnviando(false);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Gestión de Mermas</h2>
        <span className="badge-modulo">Producción / Desperdicio</span>
      </div>

      {mensaje.texto && (
        <div
          className={`alerta-sies ${mensaje.tipo}`}
          role={mensaje.tipo === 'error' ? 'alert' : 'status'}
        >
          {mensaje.texto}
        </div>
      )}

      <section className="form-card">
        <div className="form-card-header">
          <h3>Registrar merma</h3>
          <p>Asocia la cantidad sobrante al tipo y a la orden de producción.</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="merma-form-grid">
            <div className="input-group">
              <label htmlFor="merma-orden">Orden de producción *</label>
              <select
                id="merma-orden"
                name="id_produccion"
                value={formData.id_produccion}
                onChange={(event) => setFormData({
                  ...formData,
                  id_produccion: event.target.value,
                })}
                required
              >
                <option value="">Selecciona una orden</option>
                {ordenesActivas.map((orden) => (
                  <option key={orden.id_orden} value={orden.id_orden}>
                    OP-{orden.id_orden} · {orden.sku_prenda} · {orden.cantidad} unidades
                  </option>
                ))}
              </select>
            </div>

            <div className="input-group">
              <label htmlFor="merma-tipo">Tipo de merma *</label>
              <select
                id="merma-tipo"
                name="id_tipo_merma"
                value={formData.id_tipo_merma}
                onChange={(event) => setFormData({
                  ...formData,
                  id_tipo_merma: event.target.value,
                })}
                required
              >
                <option value="">Selecciona un tipo</option>
                {tipos.map((tipo) => (
                  <option key={tipo.id_tipo_merma} value={tipo.id_tipo_merma}>
                    {tipo.descripcion_merma}
                  </option>
                ))}
              </select>
            </div>

            <div className="input-group">
              <label htmlFor="merma-cantidad">Cantidad sobrante *</label>
              <input
                id="merma-cantidad"
                name="cantidad_sobrante"
                type="number"
                min="0.01"
                step="0.01"
                value={formData.cantidad_sobrante}
                onChange={(event) => setFormData({
                  ...formData,
                  cantidad_sobrante: event.target.value,
                })}
                required
              />
            </div>
          </div>
          <div className="form-actions-right">
            <button
              type="submit"
              className="btn-sies-primary"
              disabled={enviando || cargando || !ordenesActivas.length || !tipos.length}
            >
              {enviando ? 'Registrando...' : 'Registrar merma'}
            </button>
          </div>
          {!cargando && !errorLista && !ordenesActivas.length && (
            <p className="merma-ayuda" role="status">
              No hay órdenes activas disponibles para asociar.
            </p>
          )}
          {!cargando && !errorLista && !tipos.length && (
            <p className="merma-ayuda" role="status">
              No hay tipos de merma registrados en la base de datos.
            </p>
          )}
        </form>
      </section>

      <section className="merma-lista">
        <h3>Mermas registradas</h3>
        {cargando && <p role="status">Cargando mermas...</p>}
        {errorLista && <p className="merma-error" role="alert">{errorLista}</p>}
        {!cargando && !errorLista && !mermas.length && (
          <p>Aún no se han registrado mermas.</p>
        )}
        {!cargando && !errorLista && mermas.length > 0 && (
          <div className="merma-table-scroll">
            <table className="merma-table">
              <thead>
                <tr>
                  <th>Registro</th>
                  <th>Orden</th>
                  <th>Tipo de merma</th>
                  <th>Cantidad sobrante</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {mermas.map((merma) => (
                  <tr key={merma.id_merma}>
                    <td>#{merma.id_merma}</td>
                    <td>OP-{merma.id_produccion}</td>
                    <td>{merma.descripcion_tipo_merma}</td>
                    <td>{Number(merma.cantidad_sobrante).toLocaleString('es-CO')}</td>
                    <td>{fechaLegible(merma.fecha_registro)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
