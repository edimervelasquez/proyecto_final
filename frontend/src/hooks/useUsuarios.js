New-Item -Path "src\hooks\useUsuarios.js" -ItemType File -Value @"
import { useState, useEffect } from 'react';
import { authService } from '../services/authService';

export const useUsuarios = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);

  const cargarUsuarios = async () => {
    setCargando(true);
    try {
      const data = await authService.obtenerUsuarios();
      if (Array.isArray(data)) setUsuarios(data);
      else setMensaje({ texto: data.error || 'Error al cargar usuarios', tipo: 'error' });
    } catch (err) {
      setMensaje({ texto: 'Error de conexión con el servidor', tipo: 'error' });
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarUsuarios();
  }, []);

  const cambiarEstado = async (id, nuevoEstado) => {
    const res = await authService.cambiarEstado(id, nuevoEstado);
    if (res.mensaje) {
      setMensaje({ texto: res.mensaje, tipo: 'exito' });
      cargarUsuarios();
    } else {
      setMensaje({ texto: res.error, tipo: 'error' });
    }
  };

  const eliminarUsuario = async (id) => {
    if (window.confirm('¿Seguro que desea eliminar este usuario?')) {
      const res = await authService.eliminarUsuario(id);
      if (res.mensaje) {
        setMensaje({ texto: res.mensaje, tipo: 'exito' });
        cargarUsuarios();
      } else {
        setMensaje({ texto: res.error, tipo: 'error' });
      }
    }
  };

  return { usuarios, mensaje, cargando, cambiarEstado, eliminarUsuario };
};
