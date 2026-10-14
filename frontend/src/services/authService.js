import { request } from './httpClient';

export const authService = {
  login: (credentials) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  }),

  registrar: (userData) => request('/auth/registrar', {
    method: 'POST',
    body: JSON.stringify(userData),
  }),

  obtenerUsuarios: () => request('/auth/usuarios'),

  cambiarEstado: (idUsuario, estado) => request(`/auth/usuarios/${idUsuario}/estado`, {
    method: 'PUT',
    body: JSON.stringify({ estado }),
  }),

  cambiarRol: (idUsuario, id_rol) => request(`/auth/usuarios/${idUsuario}/rol`, {
    method: 'PUT',
    body: JSON.stringify({ id_rol }),
  }),

  eliminarUsuario: (idUsuario) => request(`/auth/usuarios/${idUsuario}`, {
    method: 'DELETE',
  }),
};
