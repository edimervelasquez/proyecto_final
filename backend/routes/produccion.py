from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models import FichaTecnicaInsumo, MateriaPrima, Produccion

produccion_bp = Blueprint('produccion', __name__, url_prefix='/api/produccion')

@produccion_bp.route('/orden', methods=['POST'])
def registrar_orden_produccion():
    data = request.get_json(silent=True) or {}
    
    id_area = data.get('id_area')
    sku_prenda = data.get('sku_prenda')
    cantidad_a_producir = data.get('cantidad_a_producir')
    fecha_entrega = data.get('fecha_entrega')
    id_usuario = data.get('id_usuario') or data.get('id_empleado')  # Trazabilidad del operario
    
    # Validar campos obligatorios
    if not all([id_area, sku_prenda, cantidad_a_producir, fecha_entrega]):
        return jsonify({"error": "Faltan campos obligatorios para registrar la orden."}), 400
        
    try:
        cantidad_a_producir = int(cantidad_a_producir)
        if cantidad_a_producir <= 0:
            return jsonify({"error": "La cantidad a producir debe ser mayor a cero."}), 400

        # Verificar receta / ficha técnica
        insumos_receta = FichaTecnicaInsumo.query.filter_by(sku_prenda=sku_prenda).all()
        
        if not insumos_receta:
            return jsonify({"error": f"No se encontró una Ficha Técnica registrada para el SKU: {sku_prenda}. Primero créala."}), 404
            
        # Validar stock disponible de materia prima
        for item in insumos_receta:
            material = MateriaPrima.query.get(item.id_materiaPrima)
            if not material:
                return jsonify({"error": f"El material con ID {item.id_materiaPrima} requerido por la prenda no existe en el catálogo."}), 404
                
            cantidad_requerida_total = float(item.cantidad_estimada) * cantidad_a_producir
            
            if float(material.Cantidad_materiaPrima) < cantidad_requerida_total:
                return jsonify({
                    "error": f"Falta material para la orden. El insumo '{material.nombre_material}' (ID: {material.id_materiaPrima}) tiene stock de {material.Cantidad_materiaPrima}, pero requieres {cantidad_requerida_total} para este lote."
                }), 400

        # Descontar stock de materia prima
        for item in insumos_receta:
            material = MateriaPrima.query.get(item.id_materiaPrima)
            cantidad_requerida_total = float(item.cantidad_estimada) * cantidad_a_producir
            material.Cantidad_materiaPrima = float(material.Cantidad_materiaPrima) - cantidad_requerida_total

        # Guardar la orden con trazabilidad de operario
        nueva_orden = Produccion(
            id_area=id_area,
            id_ingreso_insumos=1,
            fecha_recibido=db.func.current_date(),
            fecha_entrega=fecha_entrega,
            cantidad_recibida=cantidad_a_producir,
            cantidad_entregada=0
        )
        
        # Asignar usuario si el modelo lo soporta
        if hasattr(nueva_orden, 'id_usuario') and id_usuario:
            nueva_orden.id_usuario = id_usuario
        
        db.session.add(nueva_orden)
        db.session.commit()
        
        return jsonify({
            "mensaje": f"¡Orden de producción para {cantidad_a_producir} unidades de {sku_prenda} iniciada con éxito!",
            "estado": "Materiales descontados del inventario correctamente.",
            "registrado_por_usuario": id_usuario
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@produccion_bp.route('/actividad-reciente', methods=['GET'])
def actividad_reciente():
    """Endpoint para que el administrador monitoree las últimas órdenes creadas"""
    try:
        ordenes = Produccion.query.order_by(Produccion.id_produccion.desc()).limit(10).all()
        historial = []
        for orden in ordenes:
            historial.append({
                "id_orden": orden.id_produccion,
                "cantidad": orden.cantidad_recibida,
                "fecha_recibido": str(orden.fecha_recibido),
                "fecha_entrega": str(orden.fecha_entrega),
                "id_area": orden.id_area,
                "id_usuario": getattr(orden, 'id_usuario', 'No especificado')
            })
        return jsonify(historial), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500