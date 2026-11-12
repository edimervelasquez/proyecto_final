import { useCallback, useEffect, useState } from 'react';
import { insumoService } from '../services/insumoService';

const FORMULARIO_VACIO = {
  id_materia_prima: '',
  nombre_material: '',
  cantidad_ingresada: '',
  proveedor: '',
  costo_unitario: '',
  fecha_ingreso: '',
  stock_minimo: '0',
};

const crearMinimos = (materiales) => Object.fromEntries(
  materiales.map((material) => [
    material.id_materiaPrima,
    String(material.stock_minimo || 0),
  ]),
);

export default function useIngresoInsumos(user) {
  const [formData, setFormData] = useState(FORMULARIO_VACIO);
  const [catalogo, setCatalogo] = useState([]);
  const [ingresos, setIngresos] = useState([]);
  const [movimientos, setMovimientos] = useState([]);
  const [minimos, setMinimos] = useState({});
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);
  const [cargandoLista, setCargandoLista] = useState(true);
  const [errorLista, setErrorLista] = useState('');
  const esAdministrador = user?.id_rol === 1
    || ['administrador', 'jefe'].includes((user?.rol || '').toLowerCase());

  const cargarDatos = useCallback(() => (
    Promise.all([
      insumoService.obtenerCatalogo(),
      insumoService.obtenerIngresos(),
      insumoService.obtenerMovimientos(),
    ]).then(([materiales, registros, movimientosRegistrados]) => ({
      materiales,
      registros,
      movimientos: movimientosRegistrados,
    }))
  ), []);

  const aplicarDatos = ({ materiales, registros, movimientos: movimientosRegistrados }) => {
    setCatalogo(materiales);
    setIngresos(registros);
    setMovimientos(movimientosRegistrados);
    setMinimos(crearMinimos(materiales));
  };

  useEffect(() => {
    cargarDatos()
      .then((datos) => {
        aplicarDatos(datos);
        setErrorLista('');
        setCargandoLista(false);
      })
      .catch((error) => {
        setErrorLista(error.message || 'No se pudo cargar el inventario.');
        setCargandoLista(false);
      });
  }, [cargarDatos]);

  const handleChange = (event) => {
    setFormData((actual) => ({
      ...actual,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });

    try {
      const body = {
        ...(formData.id_materia_prima === 'nuevo'
          ? {
            nombre_material: formData.nombre_material.trim(),
            stock_minimo: Number(formData.stock_minimo || 0),
          }
          : { id_materiaPrima: Number(formData.id_materia_prima) }),
        cantidad: Number(formData.cantidad_ingresada),
        proveedor: formData.proveedor,
        costo_unitario: Number(formData.costo_unitario || 0),
        ...(formData.fecha_ingreso && { fecha_ingreso: formData.fecha_ingreso }),
      };
      const respuesta = await insumoService.registrarIngreso(body);
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      setFormData(FORMULARIO_VACIO);
      setCargandoLista(true);
      const datos = await cargarDatos();
      aplicarDatos(datos);
      setErrorLista('');
      setCargandoLista(false);
    } catch (error) {
      setMensaje({
        texto: error.message || 'No se pudo guardar el ingreso.',
        tipo: 'error',
      });
    } finally {
      setCargando(false);
    }
  };

  const guardarMinimo = async (material) => {
    setMensaje({ texto: '', tipo: '' });
    try {
      const stockMinimo = Number(minimos[material.id_materiaPrima]);
      if (!Number.isInteger(stockMinimo) || stockMinimo < 0) {
        throw new Error('El stock mínimo debe ser un entero igual o mayor que cero.');
      }
      await insumoService.actualizarStockMinimo(
        material.id_materiaPrima,
        stockMinimo,
      );
      const materiales = await insumoService.obtenerCatalogo();
      setCatalogo(materiales);
      setMinimos(crearMinimos(materiales));
      setMensaje({ texto: 'Stock mínimo actualizado.', tipo: 'exito' });
    } catch (error) {
      setMensaje({
        texto: error.message || 'No se pudo actualizar el stock mínimo.',
        tipo: 'error',
      });
    }
  };

  const filas = ingresos.map((ingreso) => ({
    ...ingreso,
    referencia: `Ingreso #${ingreso.id_ingreso}`,
    detalle: `${ingreso.insumo} · ${ingreso.cantidad} unidades · ${ingreso.proveedor || 'Sin proveedor'}`,
  }));
  const filasMovimientos = movimientos.map((movimiento) => ({
    ...movimiento,
    id: movimiento.id_movimiento,
    referencia: `${movimiento.referencia} · ${movimiento.insumo}`,
    detalle: `${movimiento.tipo_movimiento === 'ENTRADA' ? '+' : ''}${movimiento.cantidad} unidades`,
  }));

  const cambiarMinimo = (idMateriaPrima, valor) => {
    setMinimos((actuales) => ({
      ...actuales,
      [idMateriaPrima]: valor,
    }));
  };

  return {
    formData,
    catalogo,
    ingresos,
    minimos,
    mensaje,
    cargando,
    cargandoLista,
    errorLista,
    esAdministrador,
    filas,
    filasMovimientos,
    handleChange,
    handleSubmit,
    guardarMinimo,
    cambiarMinimo,
  };
}
