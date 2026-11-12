import { request } from './httpClient';

export const authService = {
  login: (credentials) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  }),

  solicitarRecuperacion: (data) => request('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  restablecerContrasena: (data) => request('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify(data),
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

  actualizarCorreoRecuperacion: (idUsuario, correo_recuperacion) => request(
    `/auth/usuarios/${idUsuario}/correo-recuperacion`,
    {
      method: 'PUT',
      body: JSON.stringify({ correo_recuperacion }),
    },
  ),

  eliminarUsuario: (idUsuario) => request(`/auth/usuarios/${idUsuario}`, {
    method: 'DELETE',
  }),
};
