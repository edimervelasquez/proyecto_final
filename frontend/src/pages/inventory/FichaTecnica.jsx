import { useCallback, useEffect, useState } from 'react';
import FormularioFicha from '../../components/forms/FormularioFicha';
import TrazabilidadTable from '../../components/TrazabilidadTable';
import { insumoService } from '../../services/insumoService';
import '../../styles/FichaTecnica.css';

const fichaVacia = () => ({
  sku_prenda: '',
  nombre_producto: '',
  descripcion: '',
  costo_mano_obra: '0',
  precio_mayorista: '',
  precio_detal: '',
  insumos: [{ id_materiaPrima: '', cantidad_estimada: '' }],
});

const FichaTecnica = () => {
  const [formData, setFormData] = useState(fichaVacia);
  const [catalogo, setCatalogo] = useState([]);
  const [fichas, setFichas] = useState([]);
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);
  const [cargandoLista, setCargandoLista] = useState(true);
  const [errorLista, setErrorLista] = useState('');

  const cargarDatos = useCallback(() => (
    Promise.all([
        insumoService.obtenerCatalogo(),
        insumoService.obtenerFichas(),
      ]).then(([materiales, registros]) => ({
        materiales,
        registros,
      }))
  ), []);

  useEffect(() => {
    cargarDatos()
      .then(({ materiales, registros }) => {
        setCatalogo(materiales);
        setFichas(registros);
        setErrorLista('');
        setCargandoLista(false);
      })
      .catch((error) => {
        setErrorLista(error.message || 'No se pudieron cargar las fichas técnicas.');
        setCargandoLista(false);
      });
  }, [cargarDatos]);

  const handleChange = (event) => {
    setFormData({ ...formData, [event.target.name]: event.target.value });
  };

  const handleInsumoChange = (index, field, value) => {
    const insumos = formData.insumos.map((item, itemIndex) => (
      itemIndex === index ? { ...item, [field]: value } : item
    ));
    setFormData({ ...formData, insumos });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setCargando(true);
    setMensaje({ texto: '', tipo: '' });
    try {
      const body = {
        sku_prenda: formData.sku_prenda.trim(),
        nombre_producto: formData.nombre_producto.trim(),
        descripcion: formData.descripcion.trim() || null,
        costo_mano_obra: Number(formData.costo_mano_obra),
        precio_mayorista: Number(formData.precio_mayorista),
        precio_detal: Number(formData.precio_detal),
        insumos: formData.insumos.map((insumo) => ({
          id_materiaPrima: Number(insumo.id_materiaPrima),
          cantidad_estimada: Number(insumo.cantidad_estimada),
        })),
      };
      const respuesta = await insumoService.crearFichaTecnica(body);
      setMensaje({ texto: respuesta.mensaje, tipo: 'exito' });
      setFormData(fichaVacia());
      setCargandoLista(true);
      const { materiales, registros } = await cargarDatos();
      setCatalogo(materiales);
      setFichas(registros);
      setErrorLista('');
      setCargandoLista(false);
    } catch (error) {
      setMensaje({
        texto: error.message || 'No se pudo guardar la ficha técnica.',
        tipo: 'error',
      });
    } finally {
      setCargando(false);
    }
  };

  const filas = fichas.map((ficha) => ({
    ...ficha,
    referencia: ficha.sku_prenda,
    detalle: `${ficha.nombre_producto}${ficha.descripcion ? ` · ${ficha.descripcion}` : ''} · ${ficha.insumos.map((item) => `${item.insumo}: ${item.cantidad_estimada}`).join(', ')}`,
  }));

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Gestión de Fichas Técnicas</h2>
        <span className="badge-modulo">Diseño y Especificaciones</span>
      </div>

      {mensaje.texto && (
        <div className={`alerta-sies ${mensaje.tipo}`} role={mensaje.tipo === 'error' ? 'alert' : 'status'}>
          {mensaje.texto}
        </div>
      )}

      <FormularioFicha
        formData={formData}
        catalogo={catalogo}
        onChange={handleChange}
        onInsumoChange={handleInsumoChange}
        onAddInsumo={() => setFormData({
          ...formData,
          insumos: [...formData.insumos, { id_materiaPrima: '', cantidad_estimada: '' }],
        })}
        onRemoveInsumo={(index) => setFormData({
          ...formData,
          insumos: formData.insumos.filter((_, itemIndex) => itemIndex !== index),
        })}
        onSubmit={handleSubmit}
        cargando={cargando || catalogo.length === 0}
      />

      <TrazabilidadTable
        titulo="Fichas técnicas registradas"
        registros={filas}
        cargando={cargandoLista}
        error={errorLista}
        vacio="Aún no se han registrado fichas técnicas."
      />
    </div>
  );
};

export default FichaTecnica;
