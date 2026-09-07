import React from 'react';
import '../styles/GestionEmpleados.css';

const TablaEmpleados = ({ usuarios, onCambiarEstado, onEliminar }) => {
  return (
    <div className="tabla-container">
      <table className="tabla-empleados">
        <thead>
          <tr>
            <th>ID</th>
            <th>Empleado</th>
            <th>Correo</th>
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
              <td>{u.cedula || 'N/A'}</td>
              <td>{u.rol || u.nombre_rol}</td>
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