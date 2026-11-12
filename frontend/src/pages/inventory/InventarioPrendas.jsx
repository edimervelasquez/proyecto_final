import TrazabilidadTable from '../../components/TrazabilidadTable';
import useInventarioPrendas from '../../hooks/useInventarioPrendas';
import '../../styles/Comercial.css';

const UBICACIONES = [
  { valor: 'BODEGA_MAYORISTA', etiqueta: 'Bodega mayorista' },
  { valor: 'BODEGA_LOCAL', etiqueta: 'Bodega del local' },
  { valor: 'LOCAL', etiqueta: 'Local / tienda' },
];

const moneda = (valor) => new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
}).format(valor || 0);

export default function InventarioPrendas({ user }) {
  const admin = user?.id_rol === 1;
  const {
    productos,
    inventario,
    movimientosTabla,
    seleccion,
    setSeleccion,
    traslado,
    setTraslado,
    inventarioInicial,
    setInventarioInicial,
    mensaje,
    cargando,
    error,
    cambiarPrecio,
    guardarPrecios,
    registrarTraslado,
    registrarInventarioInicial,
    ubicacionTieneMovimiento,
  } = useInventarioPrendas();

  return (
    <div className="view-container comercial-container">
      <div className="view-header">
        <h2>Inventario de Prendas</h2>
        <span className="badge-modulo">Bodegas / Local</span>
      </div>
      {mensaje.texto && <div className={`alerta-sies ${mensaje.tipo}`} role="status">{mensaje.texto}</div>}
      {error && <p className="trazabilidad-error" role="alert">{error}</p>}

      <section className="comercial-panel">
        <h3>Productos, precios y existencias</h3>
        {cargando ? <p>Cargando inventario...</p> : (
          <div className="comercial-tabla-scroll">
            <table className="comercial-tabla">
              <thead>
                <tr>
                  <th>Producto / SKU</th>
                  <th>Mayorista</th>
                  <th>Detal</th>
                  <th>Bodega mayorista</th>
                  <th>Bodega local</th>
                  <th>Local</th>
                  {admin && <th>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {productos.map((producto) => (
                  <tr key={producto.sku_prenda}>
                    <td>{producto.nombre_producto} · {producto.sku_prenda}</td>
                    <td>{moneda(producto.precio_mayorista)}</td>
                    <td>{moneda(producto.precio_detal)}</td>
                    <td>{producto.existencias.BODEGA_MAYORISTA || 0}</td>
                    <td>{producto.existencias.BODEGA_LOCAL || 0}</td>
                    <td>{producto.existencias.LOCAL || 0}</td>
                    {admin && (
                      <td>
                        <button
                          type="button"
                          className="comercial-action"
                          onClick={() => setSeleccion({
                            sku_prenda: producto.sku_prenda,
                            nombre_producto: producto.nombre_producto,
                            precio_mayorista: String(producto.precio_mayorista),
                            precio_detal: String(producto.precio_detal),
                            costo_mano_obra: String(producto.costo_mano_obra),
                          })}
                        >
                          Editar precios
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
                {!productos.length && (
                  <tr><td colSpan={admin ? 7 : 6}>No hay productos registrados.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {admin && seleccion && (
        <form className="comercial-panel comercial-form" onSubmit={guardarPrecios}>
          <h3>Actualizar precios · {seleccion.nombre_producto}</h3>
          <div className="comercial-form-grid">
            <label>Costo de mano de obra por unidad
              <input name="costo_mano_obra" type="number" min="0" step="0.01" value={seleccion.costo_mano_obra} onChange={cambiarPrecio} required />
            </label>
            <label>Precio mayorista
              <input name="precio_mayorista" type="number" min="0.01" step="0.01" value={seleccion.precio_mayorista} onChange={cambiarPrecio} required />
            </label>
            <label>Precio al detal
              <input name="precio_detal" type="number" min="0.01" step="0.01" value={seleccion.precio_detal} onChange={cambiarPrecio} required />
            </label>
          </div>
          <div className="comercial-actions">
            <button className="comercial-action" type="submit">Guardar</button>
            <button className="comercial-action secundario" type="button" onClick={() => setSeleccion(null)}>Cancelar</button>
          </div>
        </form>
      )}

      {admin && (
        <form className="comercial-panel comercial-form" onSubmit={registrarInventarioInicial}>
          <h3>Cargar existencias actuales</h3>
          <p className="comercial-nota">
            Para prendas que ya existían antes de usar el sistema. Solo se permite una carga inicial por producto y ubicación, antes de registrar otros movimientos.
          </p>
          <div className="comercial-form-grid">
            <label>Ubicación
              <select
                value={inventarioInicial.ubicacion}
                onChange={(event) => setInventarioInicial({
                  ...inventarioInicial,
                  ubicacion: event.target.value,
                  sku_prenda: '',
                })}
              >
                {UBICACIONES.map((ubicacion) => (
                  <option value={ubicacion.valor} key={ubicacion.valor}>{ubicacion.etiqueta}</option>
                ))}
              </select>
            </label>
            <label>Producto
              <select
                value={inventarioInicial.sku_prenda}
                onChange={(event) => setInventarioInicial({
                  ...inventarioInicial,
                  sku_prenda: event.target.value,
                })}
                required
              >
                <option value="">Selecciona producto</option>
                {productos.filter((producto) => (
                  !ubicacionTieneMovimiento(producto.sku_prenda, inventarioInicial.ubicacion)
                )).map((producto) => (
                  <option value={producto.sku_prenda} key={producto.sku_prenda}>
                    {producto.nombre_producto} · {producto.sku_prenda}
                  </option>
                ))}
              </select>
            </label>
            <label>Cantidad existente
              <input
                type="number"
                min="1"
                step="1"
                value={inventarioInicial.cantidad}
                onChange={(event) => setInventarioInicial({
                  ...inventarioInicial,
                  cantidad: event.target.value,
                })}
                required
              />
            </label>
            <label>Costo unitario estimado
              <input
                type="number"
                min="0"
                step="0.01"
                value={inventarioInicial.costo_unitario}
                onChange={(event) => setInventarioInicial({
                  ...inventarioInicial,
                  costo_unitario: event.target.value,
                })}
                required
              />
            </label>
          </div>
          <button className="comercial-action" type="submit">Registrar inventario inicial</button>
        </form>
      )}

      {admin && (
        <form className="comercial-panel comercial-form" onSubmit={registrarTraslado}>
          <h3>Trasladar prendas entre ubicaciones</h3>
          <div className="comercial-form-grid">
            <label>Producto
              <select
                value={traslado.sku_prenda}
                onChange={(event) => setTraslado({ ...traslado, sku_prenda: event.target.value })}
                required
              >
                <option value="">Selecciona producto</option>
                {productos.map((producto) => <option value={producto.sku_prenda} key={producto.sku_prenda}>{producto.nombre_producto}</option>)}
              </select>
            </label>
            <label>Origen
              <select value={traslado.ubicacion_origen} onChange={(event) => setTraslado({ ...traslado, ubicacion_origen: event.target.value })}>
                {UBICACIONES.map((ubicacion) => <option value={ubicacion.valor} key={ubicacion.valor}>{ubicacion.etiqueta}</option>)}
              </select>
            </label>
            <label>Destino
              <select value={traslado.ubicacion_destino} onChange={(event) => setTraslado({ ...traslado, ubicacion_destino: event.target.value })}>
                {UBICACIONES.map((ubicacion) => <option value={ubicacion.valor} key={ubicacion.valor}>{ubicacion.etiqueta}</option>)}
              </select>
            </label>
            <label>Cantidad
              <input type="number" min="1" step="1" value={traslado.cantidad} onChange={(event) => setTraslado({ ...traslado, cantidad: event.target.value })} required />
            </label>
          </div>
          <button className="comercial-action" type="submit">Registrar traslado</button>
        </form>
      )}

      <TrazabilidadTable
        titulo="Historial de movimientos de prendas"
        registros={movimientosTabla}
        cargando={cargando}
        error={error}
        vacio="Aún no hay movimientos de prendas."
      />
      {inventario.length > 0 && <p className="comercial-nota">Las existencias se actualizan automáticamente al aprobar calidad, trasladar prendas o registrar una venta.</p>}
    </div>
  );
}
