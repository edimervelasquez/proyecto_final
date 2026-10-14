import { request } from './httpClient';

export const insumoService = {
  obtenerCatalogo: () => request('/insumos/catalogo'),
  obtenerIngresos: () => request('/insumos/ingresos'),
  obtenerMovimientos: () => request('/insumos/movimientos'),
  obtenerAlertasStock: () => request('/insumos/alertas-stock'),
  actualizarStockMinimo: (id, stock_minimo) => request(`/insumos/${id}/stock-minimo`, {
    method: 'PUT',
    body: JSON.stringify({ stock_minimo }),
  }),
  obtenerFichas: () => request('/insumos/fichas'),
  obtenerProductos: () => request('/comercial/productos'),
  actualizarPrecios: (sku, data) => request(`/comercial/productos/${encodeURIComponent(sku)}/precios`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  registrarIngreso: (ingresoData) => request('/insumos/ingreso', {
    method: 'POST',
    body: JSON.stringify(ingresoData),
  }),

  crearFichaTecnica: (fichaData) => request('/insumos/ficha-tecnica', {
    method: 'POST',
    body: JSON.stringify(fichaData),
  }),
};
