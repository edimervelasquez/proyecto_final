import { request } from './httpClient';

export const produccionService = {
  obtenerAreas: () => request('/produccion/areas'),
  crearArea: (data) => request('/produccion/areas', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  obtenerOrdenes: () => request('/produccion/ordenes'),
  obtenerRetrasos: () => request('/produccion/retrasos'),
  registrarRetraso: (idOrden, data) => request(`/produccion/ordenes/${idOrden}/retrasos`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  reanudarProduccion: (idRetraso) => request(`/produccion/retrasos/${idRetraso}/reanudar`, {
    method: 'POST',
  }),
  registrarOrden: (data) => request('/produccion/orden', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  avanzarEtapa: (idOrden, idAreaDestino) => request(`/produccion/ordenes/${idOrden}/avanzar`, {
    method: 'POST',
    body: JSON.stringify({ id_area_destino: idAreaDestino }),
  }),
  obtenerControlesCalidad: () => request('/produccion/calidad'),
  registrarControlCalidad: (data) => request('/produccion/calidad', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};
