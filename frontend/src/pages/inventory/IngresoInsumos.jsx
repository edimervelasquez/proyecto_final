import { useState } from 'react';
import { insumoService } from '../../services/insumoService';
import FormularioIngreso from '../../components/forms/FormularioIngreso';
import '../../styles/IngresoInsumos.css';

const IngresoInsumos = () => {
  const [formData, setFormData] = useState({
    id_materia_prima: '',
    cantidad_ingresada: '',
    proveedor: '',
    costo_unitario: ''
  });
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });

    try {
      const res = await insumoService.registrarIngreso(formData);
      if (res.mensaje) {
        setMensaje({ texto: res.mensaje, tipo: 'exito' });
        setFormData({ id_materia_prima: '', cantidad_ingresada: '', proveedor: '', costo_unitario: '' });
      } else {
        setMensaje({ texto: res.error || 'Error al registrar', tipo: 'error' });
      }
    } catch {
      setMensaje({ texto: 'Error de conexión con el servidor', tipo: 'error' });
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Gestión e Ingreso de Insumos</h2>
        <span className="badge-modulo">Inventario / Materia Prima</span>
      </div>

      {mensaje.texto && (
        <div className={`alerta-sies ${mensaje.tipo}`}>
          {mensaje.texto}
        </div>
      )}

      <FormularioIngreso
        formData={formData}
        onChange={handleChange}
        onSubmit={handleSubmit}
        cargando={cargando}
      />
    </div>
  );
};

export default IngresoInsumos;