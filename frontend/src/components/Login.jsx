import { useState } from 'react';
import { ShieldCheck, Mail, Lock, User, CreditCard } from 'lucide-react';

export default function Login({ onLoginSuccess }) {
  const [esRegistro, setEsRegistro] = useState(false);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });

  // Estado Formulario Login
  const [loginData, setLoginData] = useState({
    correo_usuario: '',
    contrasenia_usuario: ''
  });

  // Estado Formulario Registro
  const [registroData, setRegistroData] = useState({
    empleado: '',
    correo_usuario: '',
    contrasenia_usuario: '',
    cedula_usuario: '',
    id_rol: 3 // Rol por defecto: TRABAJADOR
  });

  // Manejador del Login
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ texto: '', tipo: '' });

    try {
      const res = await fetch('http://127.0.0.1:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      });
      const data = await res.json();

      if (res.ok) {
        // Extrae el objeto usuario respetando la estructura del backend
        const usuarioValido = data.usuario || data;
        localStorage.setItem('sies_user', JSON.stringify(usuarioValido));
        onLoginSuccess(usuarioValido);
      } else {
        setMensaje({ texto: data.mensaje || 'Credenciales incorrectas.', tipo: 'error' });
      }
    } catch (err) {
      console.error(err);
      setMensaje({ texto: 'Error de conexión con el servidor Flask.', tipo: 'error' });
    }
  };

  // Manejador del Registro
  const handleRegistroSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ texto: '', tipo: '' });

    try {
      const res = await fetch('http://127.0.0.1:5000/api/auth/registrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registroData)
      });
      const data = await res.json();

      if (res.ok) {
        setMensaje({ texto: '¡Usuario creado con éxito! Ya puedes iniciar sesión.', tipo: 'exito' });
        setEsRegistro(false);
        setLoginData({ correo_usuario: registroData.correo_usuario, contrasenia_usuario: '' });
      } else {
        setMensaje({ texto: data.mensaje || 'Error al registrar usuario.', tipo: 'error' });
      }
    } catch (err) {
      console.error(err);
      setMensaje({ texto: 'Error de conexión con el servidor Flask.', tipo: 'error' });
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#f3f4f6' }}>
      <div style={{ background: '#fff', padding: '2rem', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', width: '100%', maxWidth: '400px' }}>
        
        {/* ENCABEZADO */}
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <ShieldCheck size={48} color="#2563eb" style={{ margin: '0 auto' }} />
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginTop: '0.5rem' }}>SIES - Creaciones Yullita</h2>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            {esRegistro ? 'Registro de Nuevo Usuario' : 'Control de Acceso al Sistema de Producción'}
          </p>
        </div>

        {/* NOTIFICACIONES / MENSAJES DE ERROR O ÉXITO */}
        {mensaje.texto && (
          <div style={{
            padding: '0.75rem',
            borderRadius: '6px',
            marginBottom: '1rem',
            fontSize: '0.875rem',
            backgroundColor: mensaje.tipo === 'error' ? '#fee2e2' : '#dcfce7',
            color: mensaje.tipo === 'error' ? '#dc2626' : '#166534'
          }}>
            {mensaje.texto}
          </div>
        )}

        {/* FORMULARIO DE INICIO DE SESIÓN */}
        {!esRegistro ? (
          <form onSubmit={handleLoginSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Correo Electrónico</label>
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #d1d5db', borderRadius: '6px', padding: '0.5rem' }}>
                <Mail size={18} color="#9ca3af" style={{ marginRight: '0.5rem' }} />
                <input
                  type="email"
                  required
                  style={{ border: 'none', outline: 'none', width: '100%' }}
                  value={loginData.correo_usuario}
                  onChange={(e) => setLoginData({ ...loginData, correo_usuario: e.target.value })}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Contraseña</label>
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #d1d5db', borderRadius: '6px', padding: '0.5rem' }}>
                <Lock size={18} color="#9ca3af" style={{ marginRight: '0.5rem' }} />
                <input
                  type="password"
                  required
                  style={{ border: 'none', outline: 'none', width: '100%' }}
                  value={loginData.contrasenia_usuario}
                  onChange={(e) => setLoginData({ ...loginData, contrasenia_usuario: e.target.value })}
                />
              </div>
            </div>

            <button type="submit" style={{ width: '100%', padding: '0.75rem', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
              Ingresar al Taller
            </button>
          </form>
        ) : (
          /* FORMULARIO DE REGISTRO */
          <form onSubmit={handleRegistroSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Nombre Completo</label>
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #d1d5db', borderRadius: '6px', padding: '0.5rem' }}>
                <User size={18} color="#9ca3af" style={{ marginRight: '0.5rem' }} />
                <input
                  type="text"
                  required
                  placeholder="Ej: Carlos Pérez"
                  style={{ border: 'none', outline: 'none', width: '100%' }}
                  value={registroData.empleado}
                  onChange={(e) => setRegistroData({ ...registroData, empleado: e.target.value })}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Cédula / Documento</label>
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #d1d5db', borderRadius: '6px', padding: '0.5rem' }}>
                <CreditCard size={18} color="#9ca3af" style={{ marginRight: '0.5rem' }} />
                <input
                  type="text"
                  required
                  placeholder="Ej: 1018222333"
                  style={{ border: 'none', outline: 'none', width: '100%' }}
                  value={registroData.cedula_usuario}
                  onChange={(e) => setRegistroData({ ...registroData, cedula_usuario: e.target.value })}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Correo Electrónico</label>
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #d1d5db', borderRadius: '6px', padding: '0.5rem' }}>
                <Mail size={18} color="#9ca3af" style={{ marginRight: '0.5rem' }} />
                <input
                  type="email"
                  required
                  placeholder="carlos@gmail.com"
                  style={{ border: 'none', outline: 'none', width: '100%' }}
                  value={registroData.correo_usuario}
                  onChange={(e) => setRegistroData({ ...registroData, correo_usuario: e.target.value })}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Contraseña</label>
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #d1d5db', borderRadius: '6px', padding: '0.5rem' }}>
                <Lock size={18} color="#9ca3af" style={{ marginRight: '0.5rem' }} />
                <input
                  type="password"
                  required
                  style={{ border: 'none', outline: 'none', width: '100%' }}
                  value={registroData.contrasenia_usuario}
                  onChange={(e) => setRegistroData({ ...registroData, contrasenia_usuario: e.target.value })}
                />
              </div>
            </div>

            <button type="submit" style={{ width: '100%', padding: '0.75rem', backgroundColor: '#16a34a', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
              Crear Cuenta
            </button>
          </form>
        )}

        {/* ENLACE PARA CONMUTAR ENTRADA / REGISTRO */}
        <div style={{ textAlign: 'center', marginTop: '1.25rem' }}>
          <button
            type="button"
            onClick={() => {
              setEsRegistro(!esRegistro);
              setMensaje({ texto: '', tipo: '' });
            }}
            style={{ background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', fontSize: '0.875rem', textDecoration: 'underline' }}
          >
            {esRegistro ? '¿Ya tienes cuenta? Inicia sesión aquí' : '¿No tienes cuenta? Regístrate aquí'}
          </button>
        </div>

      </div>
    </div>
  );
}