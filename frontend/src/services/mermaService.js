import { request } from './httpClient';

export const mermaService = {
  obtenerMermas: () => request('/produccion/mermas'),
  obtenerTipos: () => request('/produccion/tipos-merma'),
  registrarMerma: (data) => request('/produccion/mermas', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};
