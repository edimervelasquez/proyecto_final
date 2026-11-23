import { useCallback, useEffect, useState } from 'react';
import { insumoService } from '../../services/insumoService';
import FormularioIngreso from '../../components/forms/FormularioIngreso';
import TrazabilidadTable from '../../components/TrazabilidadTable';
import '../../styles/IngresoInsumos.css';

const formularioVacio = {
  id_materia_prima: '',
  nombre_material: '',
  cantidad_ingresada: '',
  proveedor: '',
  costo_unitario: '',
  fecha_ingreso: '',
  stock_minimo: '0',
};

const IngresoInsumos = ({ user }) => {
  const [formData, setFormData] = useState(formularioVacio);
  const [catalogo, setCatalogo] = useState([]);
  const [ingresos, setIngresos] = useState([]);
  const [movimientos, setMovimientos] = useState([]);
  const [minimos, setMinimos] = useState({});
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);
  const [cargandoLista, setCargandoLista] = useState(true);
  const [errorLista, setErrorLista] = useState('');
  const esAdministrador = user?.id_rol === 1
    || ['administrador', 'jefe'].includes((user?.rol || '').toLowerCase());

  const cargarDatos = useCallback(() => (
    Promise.all([
        insumoService.obtenerCatalogo(),
        insumoService.obtenerIngresos(),
        insumoService.obtenerMovimientos(),
      ]).then(([materiales, registros, movimientosRegistrados]) => ({
        materiales,
        registros,
        movimientos: movimientosRegistrados,
      }))
  ), []);

  useEffect(() => {
    cargarDatos()
      .then(({ materiales, registros, movimientos: movimientosRegistrados }) => {
        setCatalogo(materiales);
        setIngresos(registros);
        setMovimientos(movimientosRegistrados);
        setMinimos(Object.fromEntries(
          materiales.map((material) => [
            material.id_materiaPrima,
            String(material.stock_minimo || 0),
          ]),
        ));
        setErrorLista('');
        setCargandoLista(false);
      })
      .catch((error) => {
        setErrorLista(error.message || 'No se pudo cargar el inventario.');
        setCargandoLista(false);
      });
  }, [cargarDatos]);

  const handleChange = (event) => {
    setFormData({ ...formData, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });

    try {
      const body = {
        ...(formData.id_materia_prima === 'nuevo'
          ? {
            nombre_material: formData.nombre_material.trim(),
            stock_minimo: Number(formData.stock_minimo || 0),
          }
          : { id_materiaPrima: Number(formData.id_materia_prima) }),
        cantidad: Number(formData.cantidad_ingresada),
        proveedor: formData.proveedor,
        costo_unitario: Number(formData.costo_unitario || 0),
        ...(formData.fecha_ingreso && { fecha_ingreso: formData.fecha_ingreso }),
      };
      const respuesta = await insumoService.registrarIngreso(body);
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      setFormData(formularioVacio);
      setCargandoLista(true);
      const {
        materiales,
        registros,
        movimientos: movimientosRegistrados,
      } = await cargarDatos();
      setCatalogo(materiales);
      setIngresos(registros);
      setMovimientos(movimientosRegistrados);
      setMinimos(Object.fromEntries(
        materiales.map((material) => [
          material.id_materiaPrima,
          String(material.stock_minimo || 0),
        ]),
      ));
      setErrorLista('');
      setCargandoLista(false);
    } catch (error) {
      setMensaje({
        texto: error.message || 'No se pudo guardar el ingreso.',
        tipo: 'error',
      });
    } finally {
      setCargando(false);
    }
  };

  const filas = ingresos.map((ingreso) => ({
    ...ingreso,
    referencia: `Ingreso #${ingreso.id_ingreso}`,
    detalle: `${ingreso.insumo} · ${ingreso.cantidad} unidades · ${ingreso.proveedor || 'Sin proveedor'}`,
  }));
  const filasMovimientos = movimientos.map((movimiento) => ({
    ...movimiento,
    id: movimiento.id_movimiento,
    referencia: `${movimiento.referencia} · ${movimiento.insumo}`,
    detalle: `${movimiento.tipo_movimiento === 'ENTRADA' ? '+' : ''}${movimiento.cantidad} unidades`,
  }));

  const guardarMinimo = async (material) => {
    setMensaje({ texto: '', tipo: '' });
    try {
      const stockMinimo = Number(minimos[material.id_materiaPrima]);
      if (!Number.isInteger(stockMinimo) || stockMinimo < 0) {
        throw new Error('El stock mínimo debe ser un entero igual o mayor que cero.');
      }
      await insumoService.actualizarStockMinimo(
        material.id_materiaPrima,
        stockMinimo,
      );
      const materiales = await insumoService.obtenerCatalogo();
      setCatalogo(materiales);
      setMinimos(Object.fromEntries(
        materiales.map((item) => [
          item.id_materiaPrima,
          String(item.stock_minimo || 0),
        ]),
      ));
      setMensaje({ texto: 'Stock mínimo actualizado.', tipo: 'exito' });
    } catch (error) {
      setMensaje({
        texto: error.message || 'No se pudo actualizar el stock mínimo.',
        tipo: 'error',
      });
    }
  };

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
                    onChange={(event) => setMinimos({
                      ...minimos,
                      [material.id_materiaPrima]: event.target.value,
                    })}
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
