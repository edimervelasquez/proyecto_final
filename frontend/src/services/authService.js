const API_URL = 'http://127.0.0.1:8000/api/auth';

export const authService = {
  login: async (credentials) => {
    const res = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    return await res.json();
  },

  registrar: async (userData) => {
    const res = await fetch(`${API_URL}/registrar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    return await res.json();
  },

  obtenerUsuarios: async () => {
    const res = await fetch(`${API_URL}/usuarios`);
    return await res.json();
  },

  cambiarEstado: async (id_usuario, estado) => {
    const res = await fetch(`${API_URL}/usuarios/${id_usuario}/estado`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ estado })
    });
    return await res.json();
  },

  eliminarUsuario: async (id_usuario) => {
    const res = await fetch(`${API_URL}/usuarios/${id_usuario}`, {
      method: 'DELETE'
    });
    return await res.json();
  }
};