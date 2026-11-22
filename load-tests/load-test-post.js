import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = (__ENV.BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '');
const registerPath = (__ENV.K6_REGISTER_PATH || '/api/auth/registrar').replace(/^\/+/, '');
const token = __ENV.K6_TOKEN || '';

export const options = {
  vus: 1,
  iterations: 20, // Empieza con pocas para no llenar la tabla de prueba
  thresholds: {
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const url = `${baseUrl}/${registerPath}`;
  const tag = `${__VU}_${__ITER}_${Date.now()}`;

  const payload = JSON.stringify({
    correo: `k6_${tag}@test.com`,
    contrasenia: 'PruebaLoadTest2026!',
    empleado: `Usuario K6 ${tag}`,
    cedula: `9${String(Date.now()).slice(-8)}${__VU}${__ITER}`,
  });

  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = http.post(url, payload, { headers });

  check(res, {
    'creado correctamente (200 o 201)': (r) => r.status === 200 || r.status === 201,
  });

  sleep(1);
}