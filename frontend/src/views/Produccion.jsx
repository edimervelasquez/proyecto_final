import React, { useState } from 'react';
import FormularioProduccion from '../components/FormularioProduccion';
import '../styles/Produccion.css';

const Produccion = () => {
  const [formData, setFormData] = useState({
    id_ficha_tecnica: '',
    cantidad_producir: '',
    fecha_inicio: '',
    lote: ''
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
      setMensaje({ texto: 'Orden de producción registrada con éxito.', tipo: 'exito' });
      setCargando(false);
    }, 800);
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Control de Producción</h2>
        <span className="badge-modulo">Órdenes de Trabajo</span>
      </div>

      {mensaje.texto && (
        <div className={`alerta-sies ${mensaje.tipo}`}>
          {mensaje.texto}
        </div>
      )}

      <FormularioProduccion
        formData={formData}
        onChange={handleChange}
        onSubmit={handleSubmit}
        cargando={cargando}

        
      />
    </div>
  );
};



export default Produccion;