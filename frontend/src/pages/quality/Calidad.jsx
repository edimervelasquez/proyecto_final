import { useCallback, useEffect, useState } from 'react';
import FormularioCalidad from '../../components/forms/FormularioCalidad';
import TrazabilidadTable from '../../components/TrazabilidadTable';
import { produccionService } from '../../services/produccionService';
import '../../styles/Calidad.css';

const formularioVacio = {
  id_produccion: '',
  cantidad_optima: '',
  cantidad_defectuosa: '',
  observaciones: '',
};

const Calidad = () => {
  const [formData, setFormData] = useState(formularioVacio);
  const [ordenes, setOrdenes] = useState([]);
  const [ordenesEnProceso, setOrdenesEnProceso] = useState([]);
  const [controles, setControles] = useState([]);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);
  const [cargandoLista, setCargandoLista] = useState(true);
  const [errorLista, setErrorLista] = useState('');

  const cargarDatos = useCallback(() => (
    Promise.all([
        produccionService.obtenerOrdenes(),
        produccionService.obtenerControlesCalidad(),
      ]).then(([listaOrdenes, listaControles]) => ({
        listaOrdenes,
        listaControles,
      }))
  ), []);

  useEffect(() => {
    cargarDatos()
      .then(({ listaOrdenes, listaControles }) => {
        setOrdenes(listaOrdenes.filter((orden) => (
          orden.area === 'Calidad y Empaque' && orden.estado !== 'Finalizada'
        )));
        setOrdenesEnProceso(listaOrdenes.filter((orden) => (
          orden.area !== 'Calidad y Empaque' && orden.estado !== 'Finalizada'
        )));
        setControles(listaControles);
        setErrorLista('');
        setCargandoLista(false);
      })
      .catch((error) => {
        setErrorLista(error.message || 'No se pudieron cargar los controles de calidad.');
        setCargandoLista(false);
      });
  }, [cargarDatos]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await produccionService.registrarControlCalidad({
        id_produccion: Number(formData.id_produccion),
        cantidad_optima: Number(formData.cantidad_optima),
        cantidad_defectuosa: Number(formData.cantidad_defectuosa),
        observaciones: formData.observaciones.trim() || null,
      });
      setMensaje({ texto: `${respuesta.mensaje} Estado de la orden: ${respuesta.estado}`, tipo: 'exito' });
      setFormData(formularioVacio);
      setCargandoLista(true);
      const { listaOrdenes, listaControles } = await cargarDatos();
      setOrdenes(listaOrdenes.filter((orden) => (
        orden.area === 'Calidad y Empaque' && orden.estado !== 'Finalizada'
      )));
      setOrdenesEnProceso(listaOrdenes.filter((orden) => (
        orden.area !== 'Calidad y Empaque' && orden.estado !== 'Finalizada'
      )));
      setControles(listaControles);
      setErrorLista('');
      setCargandoLista(false);
    } catch (error) {
      setMensaje({
        texto: error.message || 'No se pudo registrar el control de calidad.',
        tipo: 'error',
      });
    } finally {
      setCargando(false);
    }
  };

  const filas = controles.map((control) => ({
    ...control,
    referencia: `Control #${control.id_control} · OP-${control.id_orden}`,
    detalle: `${control.cantidad_optima} aprobadas · ${control.cantidad_defectuosa} defectuosas${control.observaciones ? ` · ${control.observaciones}` : ''}`,
  }));

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Módulo de Calidad</h2>
        <span className="badge-modulo">Auditoría / Piezas</span>
      </div>

      {mensaje.texto && (
        <div className={`alerta-sies ${mensaje.tipo}`} role={mensaje.tipo === 'error' ? 'alert' : 'status'}>
          {mensaje.texto}
        </div>
      )}

      <FormularioCalidad
        formData={formData}
        ordenes={ordenes}
        ordenesEnProceso={ordenesEnProceso}
        onChange={(event) => setFormData({
          ...formData,
          [event.target.name]: event.target.value,
        })}
        onSubmit={handleSubmit}
        cargando={cargando || cargandoLista}
      />

      <TrazabilidadTable
        titulo="Inspecciones registradas"
        registros={filas}
        cargando={cargandoLista}
        error={errorLista}
        vacio="Aún no se han registrado inspecciones de calidad."
      />
    </div>
  );
};

export default Calidad;
