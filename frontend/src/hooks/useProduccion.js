import { useCallback, useEffect, useState } from 'react';
import { insumoService } from '../services/insumoService';
import { produccionService } from '../services/produccionService';

export const MOTIVOS_RETRASO = [
  'Reparación de prendas con defecto',
  'Falta de materia prima',
  'Falla de maquinaria',
  'Espera de instrucciones o aprobación',
  'Otro',
];

const FORMULARIO_VACIO = {
  sku_prenda: '',
  id_area: '',
  cantidad_a_producir: '',
  fecha_entrega: '',
  canal_destino: 'DETAL',
};

export default function useProduccion(user) {
  const [formData, setFormData] = useState(FORMULARIO_VACIO);
  const [fichas, setFichas] = useState([]);
  const [areas, setAreas] = useState([]);
  const [ordenes, setOrdenes] = useState([]);
  const [retrasos, setRetrasos] = useState([]);
  const [ordenRetraso, setOrdenRetraso] = useState('');
  const [motivoRetraso, setMotivoRetraso] = useState(MOTIVOS_RETRASO[0]);
  const [detalleRetraso, setDetalleRetraso] = useState('');
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);
  const [cargandoLista, setCargandoLista] = useState(true);
  const [errorLista, setErrorLista] = useState('');

  const puedeReportarRetraso = user?.id_rol === 1 || user?.id_rol === 2;

  const cargarDatos = useCallback(() => (
    Promise.all([
      insumoService.obtenerFichas(),
      produccionService.obtenerAreas(),
      produccionService.obtenerOrdenes(),
      produccionService.obtenerRetrasos(),
    ]).then(([fichasTecnicas, areasProduccion, registros, listaRetrasos]) => ({
      fichasTecnicas,
      areasProduccion,
      registros,
      listaRetrasos,
    }))
  ), []);

  const aplicarDatos = useCallback(({
    fichasTecnicas,
    areasProduccion,
    registros,
    listaRetrasos,
  }) => {
    setFichas(fichasTecnicas);
    setAreas(areasProduccion);
    setOrdenes(registros);
    setRetrasos(listaRetrasos);
    setFormData((actual) => {
      const corte = areasProduccion.find((area) => area.nombre_area === 'Corte');
      return actual.id_area || !corte
        ? actual
        : { ...actual, id_area: String(corte.id_area) };
    });
  }, []);

  const refrescarDatos = useCallback(async () => {
    const datos = await cargarDatos();
    aplicarDatos(datos);
    setErrorLista('');
    setCargandoLista(false);
  }, [aplicarDatos, cargarDatos]);

  useEffect(() => {
    cargarDatos()
      .then((datos) => {
        aplicarDatos(datos);
        setErrorLista('');
        setCargandoLista(false);
      })
      .catch((error) => {
        setErrorLista(error.message || 'No se pudieron cargar las órdenes de producción.');
        setCargandoLista(false);
      });
  }, [aplicarDatos, cargarDatos]);

  const manejarCambioFormulario = useCallback((event) => {
    setFormData((actual) => ({
      ...actual,
      [event.target.name]: event.target.value,
    }));
  }, []);

  const manejarAccion = useCallback(async (accion, mensajeError, alCompletar) => {
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });
    try {
      const respuesta = await accion();
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      alCompletar?.(respuesta);
      setCargandoLista(true);
      await refrescarDatos();
      return respuesta;
    } catch (error) {
      setMensaje({
        texto: error.message || mensajeError,
        tipo: 'error',
      });
      return null;
    } finally {
      setCargando(false);
    }
  }, [refrescarDatos]);

  const handleSubmit = useCallback(async (event) => {
    event.preventDefault();
    await manejarAccion(
      () => produccionService.registrarOrden({
        sku_prenda: formData.sku_prenda,
        id_area: Number(formData.id_area),
        cantidad_a_producir: Number(formData.cantidad_a_producir),
        fecha_entrega: formData.fecha_entrega,
        canal_destino: formData.canal_destino,
      }),
      'No se pudo registrar la orden.',
      () => setFormData(FORMULARIO_VACIO),
    );
  }, [formData, manejarAccion]);

  const iniciarRetraso = useCallback(async (event) => {
    event.preventDefault();
    await manejarAccion(
      () => produccionService.registrarRetraso(Number(ordenRetraso), {
        motivo: motivoRetraso,
        detalle: detalleRetraso.trim() || null,
      }),
      'No se pudo registrar el retraso.',
      () => {
        setOrdenRetraso('');
        setMotivoRetraso(MOTIVOS_RETRASO[0]);
        setDetalleRetraso('');
      },
    );
  }, [detalleRetraso, manejarAccion, motivoRetraso, ordenRetraso]);

  const reanudarOrden = useCallback(async (idRetraso) => {
    const respuesta = await manejarAccion(
      () => produccionService.reanudarProduccion(idRetraso),
      'No se pudo reanudar la orden.',
    );
    if (!respuesta) return;

    const duracionMinutos = respuesta.minutos_detenida;
    const tiempo = duracionMinutos >= 60
      ? `${Math.floor(duracionMinutos / 60)} h ${duracionMinutos % 60} min`
      : `${duracionMinutos} min`;
    setMensaje({
      texto: `${respuesta.mensaje} Tiempo detenido: ${tiempo}.`,
      tipo: 'exito',
    });
  }, [manejarAccion]);

  const avanzarOrden = useCallback(async (orden) => {
    await manejarAccion(
      () => produccionService.avanzarEtapa(
        orden.id_orden,
        orden.id_area_siguiente,
      ),
      'No se pudo avanzar la etapa.',
    );
  }, [manejarAccion]);

  const duracion = (segundos) => {
    const minutos = Math.floor(segundos / 60);
    if (minutos < 60) return `${minutos} min`;
    return `${Math.floor(minutos / 60)} h ${minutos % 60} min`;
  };

  const filas = ordenes.map((orden) => ({
    ...orden,
    referencia: `OP-${orden.id_orden}`,
    detalle: `${orden.sku_prenda} · ${orden.cantidad} unidades · ${orden.area}`,
  }));

  return {
    formData,
    fichas,
    areas,
    ordenes,
    retrasos,
    ordenRetraso,
    setOrdenRetraso,
    motivoRetraso,
    setMotivoRetraso,
    detalleRetraso,
    setDetalleRetraso,
    mensaje,
    cargando,
    cargandoLista,
    errorLista,
    puedeReportarRetraso,
    filas,
    handleSubmit,
    iniciarRetraso,
    reanudarOrden,
    avanzarOrden,
    manejarCambioFormulario,
    duracion,
  };
}
