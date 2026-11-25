import { resolveApiBaseUrl } from './resolveApiBaseUrl';

export const API_BASE_URL = resolveApiBaseUrl(
  import.meta.env.VITE_API_URL,
  window.location.hostname,
);

export const AUTH_STORAGE_KEY = 'sies_auth';
