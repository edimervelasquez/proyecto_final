import { useState } from 'react';
import axios from 'axios';
import { ShieldCheck, Lock, Mail } from 'lucide-react';

export default function Login({ onLoginSuccess }) {
  const [correo, setCorreo] = useState('');
  const [contrasenia, setContrasenia] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    axios.post('http://127.0.0.1:5000/api/auth/login', {
      correo_usuario: correo,
      contrasenia_usuario: contrasenia
    })
    .then((response) => {
      setLoading(false);
      // Guardamos los datos de la sesión en el localStorage del navegador
      localStorage.setItem('sies_user', JSON.stringify(response.data.usuario));
      // Notificamos a App.jsx que el usuario ingresó correctamente
      onLoginSuccess(response.data.usuario);
    })
    .catch((err) => {
      setLoading(false);
      setError(err.response?.data?.error || 'Error al conectar con el servidor de autenticación.');
    });
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.iconContainer}>
          <ShieldCheck size={40} color="#1e293b" />
        </div>
        <h2 style={styles.title}>SIES - Creaciones Yullita</h2>
        <p style={styles.subtitle}>Control de Acceso al Sistema de Producción</p>

        {error && <div style={styles.errorAlert}>{error}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Correo Electrónico</label>
            <div style={styles.inputWrapper}>
              <Mail size={18} color="#9ca3af" style={styles.inputIcon} />
              <input
                type="email"
                placeholder="ejemplo@yullita.com"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                style={styles.input}
                required
              />
            </div>
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Contraseña</label>
            <div style={styles.inputWrapper}>
              <Lock size={18} color="#9ca3af" style={styles.inputIcon} />
              <input
                type="password"
                placeholder="••••••••"
                value={contrasenia}
                onChange={(e) => setContrasenia(e.target.value)}
                style={styles.input}
                required
              />
            </div>
          </div>

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? 'Verificando...' : 'Ingresar al Taller'}
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  container: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f3f4f6', width: '100vw', position: 'fixed', top: 0, left: 0 },
  card: { backgroundColor: '#ffffff', padding: '40px', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', width: '100%', maxWidth: '400px', textAlign: 'center' },
  iconContainer: { backgroundColor: '#e2e8f0', width: '70px', height: '70px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' },
  title: { fontSize: '24px', fontWeight: 'bold', color: '#111827', margin: '0 0 5px' },
  subtitle: { fontSize: '14px', color: '#6b7280', margin: '0 0 25px' },
  form: { textAlign: 'left' },
  inputGroup: { marginBottom: '20px' },
  label: { display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '6px' },
  inputWrapper: { position: 'relative', display: 'flex', alignItems: 'center' },
  inputIcon: { position: 'absolute', left: '12px' },
  input: { width: '100%', padding: '10px 12px 10px 40px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px', outline: 'none' },
  button: { width: '100%', padding: '12px', backgroundColor: '#2563eb', color: '#ffffff', border: 'none', borderRadius: '6px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', marginTop: '10px' },
  errorAlert: { padding: '10px', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '6px', marginBottom: '20px', fontSize: '13px', textAlign: 'left' }
};