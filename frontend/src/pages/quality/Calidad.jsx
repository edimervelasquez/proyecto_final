import { useState } from 'react';
import FormularioCalidad from '../../components/forms/FormularioCalidad';
import '../../styles/Calidad.css';

const Calidad = () => {
  const [formData, setFormData] = useState({
    id_produccion: '',
    piezas_aprobadas: '',
    piezas_defectuosas: '',
    observaciones: ''
  });
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setCargando(true);
    setTimeout(() => {
      setMensaje({ texto: 'Inspección de calidad guardada.', tipo: 'exito' });
      setCargando(false);
    }, 800);
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Módulo de Calidad</h2>
        <span className="badge-modulo">Auditoría / Piezas</span>
      </div>

      {mensaje.texto && (
        <div className={`alerta-sies ${mensaje.tipo}`}>
          {mensaje.texto}
        </div>
      )}

      <FormularioCalidad
        formData={formData}
        onChange={handleChange}
        onSubmit={handleSubmit}
        cargando={cargando}
      />
    </div>
  );
};

export default Calidad;