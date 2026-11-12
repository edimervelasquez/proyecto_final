import { useState } from 'react';
import '../../styles/GestionEmpleados.css';

const TablaEmpleados = ({
  usuarios,
  onCambiarEstado,
  onCambiarRol,
  onActualizarCorreoRecuperacion,
  onEliminar,
}) => {
  const [correosRecuperacion, setCorreosRecuperacion] = useState({});

  return (
    <div className="tabla-container">
      <table className="tabla-empleados">
        <thead>
          <tr>
            <th>ID</th>
            <th>Empleado</th>
            <th>Correo</th>
            <th>Correo de recuperación</th>
            <th>Cédula</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((u) => (
            <tr key={u.id_usuario}>
              <td>{u.id_usuario}</td>
              <td>{u.empleado || u.nombre}</td>
              <td>{u.correo_usuario || u.correo}</td>
              <td>
                <form
                  className="correo-recuperacion-form"
                  onSubmit={(event) => {
                    event.preventDefault();
                    onActualizarCorreoRecuperacion(
                      u.id_usuario,
                      correosRecuperacion[u.id_usuario] ?? u.correo_recuperacion ?? '',
                    );
                  }}
                >
                  <input
                    type="email"
                    required
                    maxLength={254}
                    aria-label={`Correo de recuperación de ${u.empleado || u.nombre}`}
                    placeholder="persona@gmail.com"
                    value={correosRecuperacion[u.id_usuario] ?? u.correo_recuperacion ?? ''}
                    onChange={(event) => setCorreosRecuperacion({
                      ...correosRecuperacion,
                      [u.id_usuario]: event.target.value,
                    })}
                  />
                  <button type="submit" className="btn-accion btn-correo">
                    Guardar
                  </button>
                </form>
              </td>
              <td>{u.cedula || 'N/A'}</td>
              <td>
                <select
                  value={u.id_rol}
                  onChange={(event) => onCambiarRol(u.id_usuario, Number(event.target.value))}
                  aria-label={`Rol de ${u.empleado || u.nombre}`}
                >
                  <option value={1}>Administrador</option>
                  <option value={2}>Trabajador</option>
                  <option value={3}>Vendedor</option>
                </select>
              </td>
              <td>
                <span className={`badge-estado ${u.estado?.toLowerCase()}`}>
                  {u.estado}
                </span>
              </td>
              <td>
                <div className="acciones-container">
                  {u.estado === 'PENDIENTE' && (
                    <button
                      className="btn-accion btn-aprobar"
                      onClick={() => onCambiarEstado(u.id_usuario, 'APROBADO')}
                    >
                      Aprobar
                    </button>
                  )}
                  {u.estado === 'APROBADO' && (
                    <button
                      className="btn-accion btn-desactivar"
                      onClick={() => onCambiarEstado(u.id_usuario, 'INACTIVO')}
                    >
                      Desactivar
                    </button>
                  )}
                  {u.estado === 'INACTIVO' && (
                    <button
                      className="btn-accion btn-reactivar"
                      onClick={() => onCambiarEstado(u.id_usuario, 'APROBADO')}
                    >
                      Reactivar
                    </button>
                  )}
                  <button
                    className="btn-accion btn-eliminar"
                    onClick={() => onEliminar(u.id_usuario)}
                  >
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TablaEmpleados;