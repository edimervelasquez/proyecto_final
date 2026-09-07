const API_URL = 'http://127.0.0.1:5000/api';

export const insumoService = {
  registrarIngreso: async (ingresoData) => {
    const res = await fetch(`${API_URL}/insumos/ingreso`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ingresoData)
    });
    return await res.json();
  },

  crearFichaTecnica: async (fichaData) => {
    const res = await fetch(`${API_URL}/ficha-tecnica`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fichaData)
    });
    return await res.json();
  }
};