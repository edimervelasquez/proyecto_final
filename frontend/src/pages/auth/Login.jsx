import { useState } from 'react';
import {
  CreditCard,
  Eye,
  EyeOff,
  KeyRound,
  Lock,
  LogIn,
  Mail,
  PackageCheck,
  ShieldCheck,
  TrendingUp,
  User,
} from 'lucide-react';
import HangerIcon from '../../components/HangerIcon';
import analyticsIllustration from '../../assets/login-analytics.svg';
import { authService } from '../../services/authService';
import '../../styles/Login.css';

export default function Login({ onLoginSuccess }) {
  const [esRegistro, setEsRegistro] = useState(false);
  const [recuperacion, setRecuperacion] = useState(false);
  const [pasoRecuperacion, setPasoRecuperacion] = useState(1);
  const [mostrarContrasenia, setMostrarContrasenia] = useState(false);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });

  const [recuperacionData, setRecuperacionData] = useState({
    correo_acceso: '',
    correo_destino: '',
  });
  const [restablecimientoData, setRestablecimientoData] = useState({
    codigo: '',
    nueva_contrasena: '',
    confirmar_contrasena: '',
  });

  const [loginData, setLoginData] = useState({
    correo: '',
    contrasenia: ''
  });

  const [registroData, setRegistroData] = useState({
    empleado: '',
    correo: '',
    correo_recuperacion: '',
    contrasenia: '',
    cedula: '',
    id_rol: 2
  });

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ texto: '', tipo: '' });

    try {
      const data = await authService.login(loginData);
      onLoginSuccess(data);
    } catch (err) {
      console.error("Error al iniciar sesión:", err);
      setMensaje({ texto: err.message || 'No se pudo iniciar sesión.', tipo: 'error' });
    }
  };

  const handleSolicitarRecuperacion = async (e) => {
    e.preventDefault();
    setMensaje({ texto: '', tipo: '' });
    try {
      const data = await authService.solicitarRecuperacion(recuperacionData);
      setPasoRecuperacion(2);
      setMensaje({ texto: data.mensaje, tipo: 'exito' });
    } catch (err) {
      setMensaje({
        texto: err.message || 'No se pudo solicitar el código.',
        tipo: 'error',
      });
    }
  };

  const handleRestablecerContrasena = async (e) => {
    e.preventDefault();
    setMensaje({ texto: '', tipo: '' });
    if (restablecimientoData.nueva_contrasena !== restablecimientoData.confirmar_contrasena) {
      setMensaje({ texto: 'Las contraseñas no coinciden.', tipo: 'error' });
      return;
    }

    try {
      const data = await authService.restablecerContrasena({
        correo_acceso: recuperacionData.correo_acceso,
        codigo: restablecimientoData.codigo,
        nueva_contrasena: restablecimientoData.nueva_contrasena,
      });
      setRecuperacion(false);
      setPasoRecuperacion(1);
      setEsRegistro(false);
      setLoginData({
        correo: recuperacionData.correo_acceso,
        contrasenia: '',
      });
      setMensaje({ texto: data.mensaje, tipo: 'exito' });
      setRecuperacionData({ correo_acceso: '', correo_destino: '' });
      setRestablecimientoData({
        codigo: '',
        nueva_contrasena: '',
        confirmar_contrasena: '',
      });
    } catch (err) {
      setMensaje({
        texto: err.message || 'No se pudo actualizar la contraseña.',
        tipo: 'error',
      });
    }
  };

  const handleRegistroSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ texto: '', tipo: '' });

    try {
      const data = await authService.registrar(registroData);
      setMensaje({ texto: data.mensaje || '¡Usuario creado con éxito! Ya puedes iniciar sesión.', tipo: 'exito' });
      setEsRegistro(false);
      setLoginData({ correo: registroData.correo, contrasenia: '' });
    } catch (err) {
      console.error("Error al registrar usuario:", err);
      setMensaje({ texto: err.message || 'No se pudo crear la cuenta.', tipo: 'error' });
    }
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        <div className="login-branding">
          <div className="branding-header">
            <div className="brand-lockup">
              <span className="brand-symbol"><HangerIcon size={64} /></span>
              <div>
                <h1><span>S</span>IES</h1>
                <p>Sistema de Inventarios</p>
              </div>
            </div>
          </div>

          <div className="branding-main">
            <p className="branding-eyebrow">SISTEMA INTEGRAL DE GESTIÓN TEXTIL</p>
            <h2>
              Controla, Organiza y Gestiona tu Inventario de{' '}
              <span>Forma Eficiente</span>
            </h2>
            <p className="branding-description">
              Administra los procesos de tu taller desde un solo lugar.
            </p>
            <img
              className="branding-illustration"
              src={analyticsIllustration}
              alt=""
              aria-hidden="true"
            />
          </div>

          <div className="branding-footer">
            <span><PackageCheck size={21} /> Inventario <br /> en Tiempo Real</span>
            <span><ShieldCheck size={21} /> Mayor Control <br /> y Seguridad</span>
            <span><TrendingUp size={21} /> Gestión Más <br /> Eficiente</span>
          </div>
        </div>

        <div className="login-card">
          <div className="login-card-brand">
            <span className="login-card-mark"><HangerIcon size={48} /></span>
            <span className="login-card-wordmark"><span>S</span>IES</span>
          </div>
          <div className="login-header">
            <h2>
              {recuperacion
                ? 'Recuperar contraseña'
                : esRegistro
                  ? 'Crear Cuenta'
                  : 'Inicia sesión en tu cuenta'}
            </h2>
            <p>
              {recuperacion
                ? pasoRecuperacion === 1
                  ? 'Solicita un código en tu correo de recuperación registrado'
                  : 'Ingresa el código que enviamos a tu correo de recuperación'
                : esRegistro
                  ? 'Ingresa tus datos para registrarte'
                  : 'Accede al panel del taller'}
            </p>
          </div>

          {mensaje.texto && (
            <div
              className={`alert-box ${mensaje.tipo === 'error' ? 'alert-error' : 'alert-success'}`}
              role="alert"
            >
              {mensaje.texto}
            </div>
          )}

          {!recuperacion && !esRegistro ? (
            <form onSubmit={handleLoginSubmit} className="auth-form">
              <div className="form-group">
                <label className="sr-only" htmlFor="login-correo">Correo Electrónico</label>
                <div className="input-wrapper">
                  <User className="input-icon" size={19} />
                  <input
                    id="login-correo"
                    type="email"
                    required
                    autoComplete="username"
                    placeholder="Correo electrónico"
                    value={loginData.correo}
                    onChange={(e) => setLoginData({ ...loginData, correo: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="sr-only" htmlFor="login-contrasenia">Contraseña</label>
                <div className="input-wrapper">
                  <Lock className="input-icon" size={18} />
                  <input
                    id="login-contrasenia"
                    type={mostrarContrasenia ? 'text' : 'password'}
                    required
                    autoComplete="current-password"
                    placeholder="Contraseña"
                    value={loginData.contrasenia}
                    onChange={(e) => setLoginData({ ...loginData, contrasenia: e.target.value })}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    aria-label={mostrarContrasenia ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                    onClick={() => setMostrarContrasenia(!mostrarContrasenia)}
                  >
                    {mostrarContrasenia ? <EyeOff size={19} /> : <Eye size={19} />}
                  </button>
                </div>
              </div>

              <div className="form-options">
                <span><ShieldCheck size={15} /> Acceso seguro</span>
                <button
                  type="button"
                  className="recovery-link"
                  onClick={() => {
                    setRecuperacion(true);
                    setPasoRecuperacion(1);
                    setMensaje({ texto: '', tipo: '' });
                  }}
                >
                  ¿Olvidaste tu contraseña?
                </button>
              </div>

              <button type="submit" className="btn-primary">
                <span>Iniciar sesión</span>
                <LogIn size={19} />
              </button>
            </form>
          ) : recuperacion ? (
            pasoRecuperacion === 1 ? (
              <form onSubmit={handleSolicitarRecuperacion} className="auth-form recovery-form">
                <div className="form-group">
                  <label htmlFor="recuperacion-correo-acceso">
                    Correo de acceso a la plataforma (ej. usuario@yullita.com)
                  </label>
                  <div className="input-wrapper">
                    <Mail className="input-icon" size={18} />
                    <input
                      id="recuperacion-correo-acceso"
                      type="email"
                      required
                      autoComplete="username"
                      placeholder="usuario@yullita.com"
                      value={recuperacionData.correo_acceso}
                      onChange={(e) => setRecuperacionData({
                        ...recuperacionData,
                        correo_acceso: e.target.value,
                      })}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="recuperacion-correo-destino">
                    Correo electrónico real para recibir el código
                  </label>
                  <div className="input-wrapper">
                    <Mail className="input-icon" size={18} />
                    <input
                      id="recuperacion-correo-destino"
                      type="email"
                      required
                      autoComplete="email"
                      placeholder="persona@gmail.com"
                      value={recuperacionData.correo_destino}
                      onChange={(e) => setRecuperacionData({
                        ...recuperacionData,
                        correo_destino: e.target.value,
                      })}
                    />
                  </div>
                  <small>
                    Debe coincidir con el correo de recuperación registrado para tu cuenta.
                  </small>
                </div>

                <button type="submit" className="btn-recovery">
                  Enviar código de verificación
                </button>
              </form>
            ) : (
              <form onSubmit={handleRestablecerContrasena} className="auth-form recovery-form">
                <div className="form-group">
                  <label htmlFor="recuperacion-codigo">Código de 6 dígitos</label>
                  <div className="input-wrapper">
                    <KeyRound className="input-icon" size={18} />
                    <input
                      id="recuperacion-codigo"
                      type="text"
                      inputMode="numeric"
                      pattern="[0-9]{6}"
                      maxLength={6}
                      required
                      autoComplete="one-time-code"
                      placeholder="123456"
                      value={restablecimientoData.codigo}
                      onChange={(e) => setRestablecimientoData({
                        ...restablecimientoData,
                        codigo: e.target.value.replace(/\D/g, '').slice(0, 6),
                      })}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="recuperacion-nueva-contrasena">Nueva contraseña</label>
                  <div className="input-wrapper">
                    <Lock className="input-icon" size={18} />
                    <input
                      id="recuperacion-nueva-contrasena"
                      type="password"
                      minLength={12}
                      maxLength={128}
                      required
                      autoComplete="new-password"
                      placeholder="••••••••"
                      value={restablecimientoData.nueva_contrasena}
                      onChange={(e) => setRestablecimientoData({
                        ...restablecimientoData,
                        nueva_contrasena: e.target.value,
                      })}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="recuperacion-confirmar-contrasena">
                    Confirmar nueva contraseña
                  </label>
                  <div className="input-wrapper">
                    <Lock className="input-icon" size={18} />
                    <input
                      id="recuperacion-confirmar-contrasena"
                      type="password"
                      minLength={12}
                      maxLength={128}
                      required
                      autoComplete="new-password"
                      placeholder="••••••••"
                      value={restablecimientoData.confirmar_contrasena}
                      onChange={(e) => setRestablecimientoData({
                        ...restablecimientoData,
                        confirmar_contrasena: e.target.value,
                      })}
                    />
                  </div>
                </div>

                <button type="submit" className="btn-recovery">
                  Actualizar contraseña
                </button>
              </form>
            )
          ) : (
            <form onSubmit={handleRegistroSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="registro-empleado">Nombre Completo</label>
                <div className="input-wrapper">
                  <User className="input-icon" size={18} />
                  <input
                    id="registro-empleado"
                    type="text"
                    required
                    placeholder="Ej: Carlos Pérez"
                    value={registroData.empleado}
                    onChange={(e) => setRegistroData({ ...registroData, empleado: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="registro-cedula">Cédula / Documento</label>
                <div className="input-wrapper">
                  <CreditCard className="input-icon" size={18} />
                  <input
                    id="registro-cedula"
                    type="text"
                    required
                    placeholder="Ej: 1018222333"
                    value={registroData.cedula}
                    onChange={(e) => setRegistroData({ ...registroData, cedula: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="registro-correo">Correo de acceso a la plataforma</label>
                <div className="input-wrapper">
                  <Mail className="input-icon" size={18} />
                  <input
                    id="registro-correo"
                    type="email"
                    required
                    placeholder="usuario@yullita.com"
                    value={registroData.correo}
                    onChange={(e) => setRegistroData({ ...registroData, correo: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="registro-correo-recuperacion">
                  Correo real para recuperar la contraseña
                </label>
                <div className="input-wrapper">
                  <Mail className="input-icon" size={18} />
                  <input
                    id="registro-correo-recuperacion"
                    type="email"
                    required
                    placeholder="carlos@gmail.com"
                    value={registroData.correo_recuperacion}
                    onChange={(e) => setRegistroData({
                      ...registroData,
                      correo_recuperacion: e.target.value,
                    })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="registro-contrasenia">Contraseña</label>
                <div className="input-wrapper">
                  <Lock className="input-icon" size={18} />
                  <input
                    id="registro-contrasenia"
                    type="password"
                    required
                    minLength={12}
                    maxLength={128}
                    placeholder="••••••••"
                    value={registroData.contrasenia}
                    onChange={(e) => setRegistroData({ ...registroData, contrasenia: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="registro-rol">Rol solicitado</label>
                <select
                  id="registro-rol"
                  value={registroData.id_rol}
                  onChange={(e) => setRegistroData({
                    ...registroData,
                    id_rol: Number(e.target.value),
                  })}
                >
                  <option value={2}>Trabajador</option>
                  <option value={3}>Vendedor</option>
                </select>
                <small>El administrador debe aprobar la cuenta antes de ingresar.</small>
              </div>

              <button type="submit" className="btn-success">
                Crear Cuenta
              </button>
            </form>
          )}

          <div className="toggle-auth">
            {recuperacion ? (
              <button
                type="button"
                onClick={() => {
                  setRecuperacion(false);
                  setPasoRecuperacion(1);
                  setMensaje({ texto: '', tipo: '' });
                }}
              >
                Volver al inicio de sesión
              </button>
            ) : (
              <button
                type="button"
                onClick={() => {
                  setEsRegistro(!esRegistro);
                  setMensaje({ texto: '', tipo: '' });
                }}
              >
                {esRegistro ? '¿Ya tienes cuenta? Inicia sesión aquí' : '¿No tienes cuenta? Regístrate aquí'}
              </button>
            )}
          </div>
          <div className="login-card-footer">
            <span>SIES</span>
            <i aria-hidden="true">•</i>
            <span>Sistema de Inventarios</span>
          </div>
        </div>

      </div>
    </div>
  );
}
