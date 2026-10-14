import { request } from './httpClient';

export const comercialService = {
  obtenerInventario: () => request('/inventario'),
  obtenerMovimientos: () => request('/inventario/movimientos'),
  registrarInventarioInicial: (data) => request('/inventario/inicial', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  trasladar: (data) => request('/inventario/traslados', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  obtenerVentas: () => request('/ventas'),
  registrarVenta: (data) => request('/ventas', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};
