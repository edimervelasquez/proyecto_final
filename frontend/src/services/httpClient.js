import { API_BASE_URL, AUTH_STORAGE_KEY } from '../config/api';

const getToken = () => {
  const auth = JSON.parse(localStorage.getItem(AUTH_STORAGE_KEY) || 'null');
  return auth?.access_token || '';
};

export const request = async (path, options = {}) => {
  const headers = new Headers(options.headers || {});
  headers.set('Content-Type', 'application/json');

  const token = getToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || data.error || data.mensaje || 'Error en la solicitud');
  }

  return data;
};
