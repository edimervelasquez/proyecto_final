import React, { useState } from 'react';
import FormularioFicha from '../components/FormularioFicha';
import '../styles/FichaTecnica.css';

const FichaTecnica = () => {
  const [formData, setFormData] = useState({
    nombre_producto: '',
    id_materia_prima: '',
    cantidad_requerida: '',
    descripcion: ''
  });
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setCargando(true);
    // Lógica de consumo de API
    setTimeout(() => {
      setMensaje({ texto: 'Ficha técnica creada correctamente.', tipo: 'exito' });
      setCargando(false);
    }, 800);
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Gestión de Fichas Técnicas</h2>
        <span className="badge-modulo">Diseño y Especificaciones</span>
      </div>

      {mensaje.texto && (
        <div className={`alerta-sies ${mensaje.tipo}`}>
          {mensaje.texto}
        </div>
      )}

      <FormularioFicha
        formData={formData}
        onChange={handleChange}
        onSubmit={handleSubmit}
        cargando={cargando}
      />
    </div>
  );
};

export default FichaTecnica;