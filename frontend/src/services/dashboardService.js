import { request } from './httpClient';

export const dashboardService = {
  obtenerResumen: () => request('/dashboard/resumen'),
};
