import { request } from './httpClient';

export const insumoService = {
  registrarIngreso: (ingresoData) => request('/insumos/ingreso', {
    method: 'POST',
    body: JSON.stringify(ingresoData),
  }),

  crearFichaTecnica: (fichaData) => request('/insumos/ficha-tecnica', {
    method: 'POST',
    body: JSON.stringify(fichaData),
  }),
};
