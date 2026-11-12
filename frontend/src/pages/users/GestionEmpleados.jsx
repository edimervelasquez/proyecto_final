import { useEffect, useState } from 'react';
import { authService } from '../../services/authService';
import TablaEmpleados from '../../components/users/TablaEmpleados';
import '../../styles/GestionEmpleados.css';

const GestionEmpleados = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);

  const cargarUsuarios = async () => {
    setCargando(true);
    try {
      const data = await authService.obtenerUsuarios();
      if (Array.isArray(data)) setUsuarios(data);
      else setMensaje({ texto: data.error || 'Error al cargar usuarios', tipo: 'error' });
    } catch {
      setMensaje({ texto: 'Error de conexión', tipo: 'error' });
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    Promise.resolve().then(cargarUsuarios);
  }, []);

  const cambiarEstado = async (id, nuevoEstado) => {
    const res = await authService.cambiarEstado(id, nuevoEstado);
    if (res.mensaje) {
      setMensaje({ texto: res.mensaje, tipo: 'exito' });
      cargarUsuarios();
    }
  };

  const cambiarRol = async (id, idRol) => {
    try {
      const res = await authService.cambiarRol(id, idRol);
      setMensaje({ texto: res.mensaje, tipo: 'exito' });
      await cargarUsuarios();
    } catch (error) {
      setMensaje({ texto: error.message || 'No se pudo cambiar el rol.', tipo: 'error' });
    }
  };

  const actualizarCorreoRecuperacion = async (id, correo) => {
    try {
      const res = await authService.actualizarCorreoRecuperacion(id, correo);
      setMensaje({ texto: res.mensaje, tipo: 'exito' });
      await cargarUsuarios();
    } catch (error) {
      setMensaje({
        texto: error.message || 'No se pudo actualizar el correo de recuperación.',
        tipo: 'error',
      });
    }
  };

  const eliminarUsuario = async (id) => {
    if (window.confirm('¿Seguro que desea eliminar este usuario?')) {
      const res = await authService.eliminarUsuario(id);
      if (res.mensaje) {
        setMensaje({ texto: res.mensaje, tipo: 'exito' });
        cargarUsuarios();
      }
    }
  };

  return (
    <div className="gestion-container">
      <h2>Gestión y Aprobación de Empleados</h2>

      {mensaje.texto && <div className={`alerta ${mensaje.tipo}`}>{mensaje.texto}</div>}

      {cargando ? (
        <p>Cargando empleados...</p>
      ) : (
        <TablaEmpleados
          usuarios={usuarios}
          onCambiarEstado={cambiarEstado}
          onCambiarRol={cambiarRol}
          onActualizarCorreoRecuperacion={actualizarCorreoRecuperacion}
          onEliminar={eliminarUsuario}
        />
      )}
    </div>
  );
};

export default GestionEmpleados;