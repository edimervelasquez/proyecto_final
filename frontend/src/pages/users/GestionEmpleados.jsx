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
          onEliminar={eliminarUsuario}
        />
      )}
    </div>
  );
};

export default GestionEmpleados;