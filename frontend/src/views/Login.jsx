import { useState } from 'react';
import { ShieldCheck, Mail, Lock, User, CreditCard } from 'lucide-react';
import '../styles/components/Login.css';

export default function Login({ onLoginSuccess }) {
  const [esRegistro, setEsRegistro] = useState(false);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });

  const [loginData, setLoginData] = useState({
    correo_usuario: '',
    contrasenia_usuario: ''
  });

  const [registroData, setRegistroData] = useState({
    empleado: '',
    correo_usuario: '',
    contrasenia_usuario: '',
    cedula_usuario: '',
    id_rol: 3
  });

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
        const usuarioValido = data.usuario || data;
        localStorage.setItem('sies_user', JSON.stringify(usuarioValido));
        onLoginSuccess(usuarioValido);
      } else {
        setMensaje({ texto: data.mensaje || 'Credenciales incorrectas.', tipo: 'error' });
      }
    } catch (err) {
      setMensaje({ texto: 'Error de conexión con el servidor Flask.', tipo: 'error' });
    }
  };

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
      setMensaje({ texto: 'Error de conexión con el servidor Flask.', tipo: 'error' });
    }
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        
        {/* PANEL IZQUIERDO - BRANDING */}
        <div className="login-branding">
          <div className="branding-header">
            <ShieldCheck size={56} color="#f59e0b" />
            <h1>SIES Textil</h1>
            <p>Sistema Integral de Gestión y Control de Producción</p>
          </div>

          <div className="branding-features">
            <div className="feature-item">
              <span className="feature-bullet"></span>
              <span>Control detallado de insumos y materia prima</span>
            </div>
            <div className="feature-item">
              <span className="feature-bullet"></span>
              <span>Monitoreo de trazabilidad y fichas técnicas</span>
            </div>
            <div className="feature-item">
              <span className="feature-bullet"></span>
              <span>Seguimiento de módulos y órdenes de producción</span>
            </div>
            <div className="feature-item">
              <span className="feature-bullet"></span>
              <span>Auditoría de calidad y gestión de personal</span>
            </div>
          </div>

          <div className="branding-footer">
            <p>© 2026 Creaciones Yuyita. Todos los derechos reservados.</p>
          </div>
        </div>

        {/* PANEL DERECHO - FORMULARIO */}
        <div className="login-card">
          <div className="login-header">
            <h2>{esRegistro ? 'Crear Cuenta' : 'Iniciar Sesión'}</h2>
            <p>{esRegistro ? 'Ingresa tus datos para registrarte' : 'Accede al panel del taller'}</p>
          </div>

          {mensaje.texto && (
            <div className={`alert-box ${mensaje.tipo === 'error' ? 'alert-error' : 'alert-success'}`}>
              {mensaje.texto}
            </div>
          )}

          {!esRegistro ? (
            <form onSubmit={handleLoginSubmit} className="auth-form">
              <div className="form-group">
                <label>Correo Electrónico</label>
                <div className="input-wrapper">
                  <Mail className="input-icon" size={18} />
                  <input
                    type="email"
                    required
                    placeholder="ejemplo@yuyita.com"
                    value={loginData.correo_usuario}
                    onChange={(e) => setLoginData({ ...loginData, correo_usuario: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Contraseña</label>
                <div className="input-wrapper">
                  <Lock className="input-icon" size={18} />
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    value={loginData.contrasenia_usuario}
                    onChange={(e) => setLoginData({ ...loginData, contrasenia_usuario: e.target.value })}
                  />
                </div>
              </div>

              <button type="submit" className="btn-primary">
                Ingresar al Taller
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegistroSubmit} className="auth-form">
              <div className="form-group">
                <label>Nombre Completo</label>
                <div className="input-wrapper">
                  <User className="input-icon" size={18} />
                  <input
                    type="text"
                    required
                    placeholder="Ej: Carlos Pérez"
                    value={registroData.empleado}
                    onChange={(e) => setRegistroData({ ...registroData, empleado: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Cédula / Documento</label>
                <div className="input-wrapper">
                  <CreditCard className="input-icon" size={18} />
                  <input
                    type="text"
                    required
                    placeholder="Ej: 1018222333"
                    value={registroData.cedula_usuario}
                    onChange={(e) => setRegistroData({ ...registroData, cedula_usuario: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Correo Electrónico</label>
                <div className="input-wrapper">
                  <Mail className="input-icon" size={18} />
                  <input
                    type="email"
                    required
                    placeholder="carlos@gmail.com"
                    value={registroData.correo_usuario}
                    onChange={(e) => setRegistroData({ ...registroData, correo_usuario: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Contraseña</label>
                <div className="input-wrapper">
                  <Lock className="input-icon" size={18} />
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    value={registroData.contrasenia_usuario}
                    onChange={(e) => setRegistroData({ ...registroData, contrasenia_usuario: e.target.value })}
                  />
                </div>
              </div>

              <button type="submit" className="btn-success">
                Crear Cuenta
              </button>
            </form>
          )}

          <div className="toggle-auth">
            <button
              type="button"
              onClick={() => {
                setEsRegistro(!esRegistro);
                setMensaje({ texto: '', tipo: '' });
              }}
            >
              {esRegistro ? '¿Ya tienes cuenta? Inicia sesión aquí' : '¿No tienes cuenta? Regístrate aquí'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}