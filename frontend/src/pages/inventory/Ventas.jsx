import { useCallback, useEffect, useState } from 'react';
import { comercialService } from '../../services/comercialService';
import { insumoService } from '../../services/insumoService';
import '../../styles/Comercial.css';

const moneda = (valor) => new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
}).format(valor || 0);

const fecha = (valor) => valor
  ? new Date(valor).toLocaleString('es-CO')
  : 'Sin fecha';

export default function Ventas() {
  const [productos, setProductos] = useState([]);
  const [ventas, setVentas] = useState([]);
  const [canal, setCanal] = useState('DETAL');
  const [cliente, setCliente] = useState('');
  const [lineas, setLineas] = useState([
    { sku_prenda: '', cantidad: '' },
  ]);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  const cargar = useCallback(() => Promise.all([
    insumoService.obtenerProductos(),
    comercialService.obtenerVentas(),
  ]), []);

  useEffect(() => {
    cargar().then(([listaProductos, listaVentas]) => {
      setProductos(listaProductos);
      setVentas(listaVentas);
      setError('');
      setCargando(false);
    }).catch((err) => {
      setError(err.message || 'No se pudieron cargar productos y ventas.');
      setCargando(false);
    });
  }, [cargar]);

  const cambiarLinea = (index, field, value) => {
    setLineas((actuales) => actuales.map((linea, i) => (
      i === index ? { ...linea, [field]: value } : linea
    )));
  };

  const registrar = async (event) => {
    event.preventDefault();
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await comercialService.registrarVenta({
        canal,
        cliente: cliente.trim(),
        detalles: lineas.map((linea) => ({
          sku_prenda: linea.sku_prenda,
          cantidad: Number(linea.cantidad),
        })),
      });
      setMensaje({
        texto: `${respuesta.mensaje} Total: ${moneda(respuesta.total)}.`,
        tipo: 'exito',
      });
      setCliente('');
      setLineas([{ sku_prenda: '', cantidad: '' }]);
      setCargando(true);
      const [listaProductos, listaVentas] = await cargar();
      setProductos(listaProductos);
      setVentas(listaVentas);
      setCargando(false);
    } catch (err) {
      setMensaje({ texto: err.message || 'No se pudo registrar la venta.', tipo: 'error' });
    }
  };

  const ubicacionVenta = canal === 'MAYORISTA' ? 'BODEGA_MAYORISTA' : 'LOCAL';
  const productoSeleccionado = (sku) => productos.find((producto) => producto.sku_prenda === sku);

  return (
    <div className="view-container comercial-container">
      <div className="view-header">
        <h2>Ventas</h2>
        <span className="badge-modulo">Mayorista / Detal</span>
      </div>

      {mensaje.texto && <div className={`alerta-sies ${mensaje.tipo}`} role="status">{mensaje.texto}</div>}
      {error && <p className="trazabilidad-error" role="alert">{error}</p>}

      <form className="comercial-panel comercial-form" onSubmit={registrar}>
        <h3>Registrar venta</h3>
        <div className="comercial-form-grid">
          <label>Canal de venta
            <select value={canal} onChange={(event) => setCanal(event.target.value)}>
              <option value="DETAL">Al detal · existencia del local</option>
              <option value="MAYORISTA">Al por mayor · bodega mayorista</option>
            </select>
          </label>
          <label>Cliente
            <input value={cliente} onChange={(event) => setCliente(event.target.value)} required maxLength="150" />
          </label>
        </div>

        {lineas.map((linea, index) => {
          const producto = productoSeleccionado(linea.sku_prenda);
          const precio = producto
            ? (canal === 'MAYORISTA' ? producto.precio_mayorista : producto.precio_detal)
            : 0;
          const disponible = producto?.existencias?.[ubicacionVenta] || 0;
          return (
            <div className="comercial-form-grid venta-linea" key={`linea-${index}`}>
              <label>Prenda
                <select
                  value={linea.sku_prenda}
                  onChange={(event) => cambiarLinea(index, 'sku_prenda', event.target.value)}
                  required
                >
                  <option value="">Selecciona una prenda</option>
                  {productos.map((item) => (
                    <option
                      key={item.sku_prenda}
                      value={item.sku_prenda}
                      disabled={(item.existencias?.[ubicacionVenta] || 0) < 1}
                    >
                      {item.nombre_producto} · {item.sku_prenda} · disp. {item.existencias?.[ubicacionVenta] || 0}
                    </option>
                  ))}
                </select>
              </label>
              <label>Cantidad
                <input
                  type="number"
                  min="1"
                  max={disponible || undefined}
                  step="1"
                  value={linea.cantidad}
                  onChange={(event) => cambiarLinea(index, 'cantidad', event.target.value)}
                  required
                />
              </label>
              <div className="venta-precio">
                <span>Precio unitario: {moneda(precio)}</span>
                <span>Disponible: {disponible}</span>
              </div>
              {lineas.length > 1 && (
                <button
                  className="comercial-action secundario"
                  type="button"
                  onClick={() => setLineas((actuales) => actuales.filter((_, i) => i !== index))}
                >
                  Quitar
                </button>
              )}
            </div>
          );
        })}

        <div className="comercial-actions">
          <button
            className="comercial-action secundario"
            type="button"
            onClick={() => setLineas((actuales) => [...actuales, { sku_prenda: '', cantidad: '' }])}
          >
            Agregar otra prenda
          </button>
          <button className="comercial-action" type="submit" disabled={cargando}>
            {cargando ? 'Guardando...' : 'Registrar venta'}
          </button>
        </div>
      </form>

      <section className="comercial-panel">
        <h3>Ventas recientes</h3>
        {cargando ? <p>Cargando ventas...</p> : ventas.length ? (
          <div className="comercial-lista">
            {ventas.map((venta) => (
              <article className="comercial-venta" key={venta.id_venta}>
                <div>
                  <strong>Venta #{venta.id_venta} · {venta.canal} · {venta.cliente}</strong>
                  <span>{fecha(venta.fecha_venta)} · Registró {venta.registrado_por}</span>
                  <span>{venta.detalles.map((detalle) => `${detalle.sku_prenda} × ${detalle.cantidad}`).join(', ')}</span>
                </div>
                <strong>{moneda(venta.total)}</strong>
              </article>
            ))}
          </div>
        ) : <p>No hay ventas registradas.</p>}
      </section>
    </div>
  );
}
