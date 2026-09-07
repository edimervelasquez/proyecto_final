from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models import IngresoInsumos, MateriaPrima, FichaTecnicaInsumo

insumos_bp = Blueprint('insumos', __name__, url_prefix='/api')

@insumos_bp.route('/insumos/ingreso', methods=['POST'])
def registrar_ingreso_insumo():
    data = request.get_json(silent=True) or {}
    
    id_mp = data.get('id_materiaPrima')
    cantidad = data.get('cantidad')
    
    # Validar campos obligatorios
    if not id_mp or cantidad is None:
        return jsonify({"error": "Datos incompletos. Se requiere 'id_materiaPrima' y 'cantidad'."}), 400
    
    try:
        cantidad = float(cantidad)
        if cantidad <= 0:
            return jsonify({"error": "La cantidad ingresada debe ser mayor a cero."}), 400

        nuevo_ingreso = IngresoInsumos(
            id_materiaPrima=id_mp,
            cantidad_materia_prima=cantidad,
            proveedor=data.get('proveedor', 'Proveedor Genérico'),
            costo_unitario=data.get('costo_unitario', 0.0),
            fecha_ingreso=data.get('fecha_ingreso') or db.func.current_date()
        )
        db.session.add(nuevo_ingreso)
        
        # Incrementar el stock existente en el catálogo
        material = MateriaPrima.query.get(id_mp)
        if material:
            material.Cantidad_materiaPrima = float(material.Cantidad_materiaPrima or 0) + cantidad
        else:
            return jsonify({"error": "La materia prima especificada no existe en el catálogo."}), 404
        
        db.session.commit()
        
        return jsonify({
            "mensaje": "Ingreso de materia prima registrado correctamente.",
            "nuevo_stock": material.Cantidad_materiaPrima
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@insumos_bp.route('/ficha-tecnica', methods=['POST'])
def crear_ficha_tecnica():
    data = request.get_json(silent=True) or {}
    
    sku_prenda = data.get('sku_prenda')
    insumos = data.get('insumos', [])
    costo_mano_obra = float(data.get('costo_mano_obra', 0.0))
    
    # Validar campos obligatorios
    if not sku_prenda or not insumos:
        return jsonify({"error": "Datos incompletos. Se requiere SKU de prenda e insumos."}), 400
        
    try:
        costo_total_insumos = 0.0
        detalles_guardados = []
        
        for insumo in insumos:
            id_mp = insumo.get('id_materiaPrima')
            cant = float(insumo.get('cantidad_estimada', 0.0))
            
            if not id_mp or cant <= 0:
                return jsonify({"error": "Cada insumo requiere un id_materiaPrima válido y una cantidad mayor a cero."}), 400
            
            # Buscar el último costo unitario registrado
            ultimo_ingreso = IngresoInsumos.query.filter_by(id_materiaPrima=id_mp).order_by(IngresoInsumos.id_entrante.desc()).first()
            precio_unitario = float(ultimo_ingreso.costo_unitario) if ultimo_ingreso and ultimo_ingreso.costo_unitario else 5000.0
            
            costo_parcial = cant * precio_unitario
            costo_total_insumos += costo_parcial
            
            nueva_linea = FichaTecnicaInsumo(
                sku_prenda=sku_prenda,
                id_materiaPrima=id_mp,
                cantidad_estimada=cant
            )
            db.session.add(nueva_linea)
            detalles_guardados.append({
                "id_materiaPrima": id_mp,
                "cantidad": cant,
                "costo_estimado": costo_parcial
            })
            
        costo_fabricacion_base = costo_total_insumos + costo_mano_obra
        
        if costo_fabricacion_base <= 0:
            return jsonify({"error": "El costo base de fabricación no puede ser cero."}), 400
            
        db.session.commit()
        
        return jsonify({
            "mensaje": f"Ficha técnica para {sku_prenda} guardada con éxito.",
            "costo_materiales": costo_total_insumos,
            "costo_mano_obra": costo_mano_obra,
            "costo_total_fabricacion": costo_fabricacion_base,
            "detalles": detalles_guardados
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500