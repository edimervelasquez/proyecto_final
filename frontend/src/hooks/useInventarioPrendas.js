import { useCallback, useEffect, useState } from 'react';
import { comercialService } from '../services/comercialService';
import { insumoService } from '../services/insumoService';

const TRASLADO_INICIAL = {
  sku_prenda: '',
  ubicacion_origen: 'BODEGA_LOCAL',
  ubicacion_destino: 'LOCAL',
  cantidad: '',
};

const INVENTARIO_INICIAL = {
  sku_prenda: '',
  ubicacion: 'BODEGA_LOCAL',
  cantidad: '',
  costo_unitario: '',
};

export default function useInventarioPrendas() {
  const [productos, setProductos] = useState([]);
  const [inventario, setInventario] = useState([]);
  const [movimientos, setMovimientos] = useState([]);
  const [seleccion, setSeleccion] = useState(null);
  const [traslado, setTraslado] = useState(TRASLADO_INICIAL);
  const [inventarioInicial, setInventarioInicial] = useState(INVENTARIO_INICIAL);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  const cargar = useCallback(() => Promise.all([
    insumoService.obtenerProductos(),
    comercialService.obtenerInventario(),
    comercialService.obtenerMovimientos(),
  ]), []);

  const aplicarDatos = ([listaProductos, listaInventario, listaMovimientos]) => {
    setProductos(listaProductos);
    setInventario(listaInventario);
    setMovimientos(listaMovimientos);
    setError('');
  };

  useEffect(() => {
    cargar().then((datos) => {
      aplicarDatos(datos);
      setCargando(false);
    }).catch((err) => {
      setError(err.message || 'No se pudo cargar el inventario.');
      setCargando(false);
    });
  }, [cargar]);

  const cambiarPrecio = (event) => {
    setSeleccion((actual) => ({
      ...actual,
      [event.target.name]: event.target.value,
    }));
  };

  const actualizarListas = async () => {
    aplicarDatos(await cargar());
  };

  const guardarPrecios = async (event) => {
    event.preventDefault();
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await insumoService.actualizarPrecios(
        seleccion.sku_prenda,
        {
          precio_mayorista: Number(seleccion.precio_mayorista),
          precio_detal: Number(seleccion.precio_detal),
          costo_mano_obra: Number(seleccion.costo_mano_obra),
        },
      );
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      setSeleccion(null);
      await actualizarListas();
    } catch (err) {
      setMensaje({ texto: err.message || 'No se pudieron guardar los precios.', tipo: 'error' });
    }
  };

  const registrarTraslado = async (event) => {
    event.preventDefault();
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await comercialService.trasladar({
        ...traslado,
        cantidad: Number(traslado.cantidad),
      });
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      setTraslado((actual) => ({ ...actual, cantidad: '' }));
      await actualizarListas();
    } catch (err) {
      setMensaje({ texto: err.message || 'No se pudo realizar el traslado.', tipo: 'error' });
    }
  };

  const registrarInventarioInicial = async (event) => {
    event.preventDefault();
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await comercialService.registrarInventarioInicial({
        ...inventarioInicial,
        cantidad: Number(inventarioInicial.cantidad),
        costo_unitario: Number(inventarioInicial.costo_unitario),
      });
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      setInventarioInicial((actual) => ({
        ...actual,
        cantidad: '',
        costo_unitario: '',
      }));
      await actualizarListas();
    } catch (err) {
      setMensaje({
        texto: err.message || 'No se pudo registrar el inventario inicial.',
        tipo: 'error',
      });
    }
  };

  const ubicacionTieneMovimiento = (sku, ubicacion) => movimientos.some(
    (movimiento) => movimiento.sku_prenda === sku && movimiento.ubicacion === ubicacion,
  );

  const movimientosTabla = movimientos.map((movimiento) => ({
    ...movimiento,
    referencia: `${movimiento.tipo} · ${movimiento.referencia || ''}`,
    detalle: `${movimiento.producto} · ${movimiento.cantidad} unidades · ${movimiento.ubicacion}`,
    fecha_registro: movimiento.fecha,
    proceso: movimiento.ubicacion,
    estado: movimiento.tipo,
  }));

  return {
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
  };
}
