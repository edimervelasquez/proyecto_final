from flask import Blueprint, jsonify
from backend.models.models import Produccion

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/rendimiento', methods=['GET'])
def obtener_rendimiento():
    try:
        ordenes = Produccion.query.all()
        
        total_recibido = sum(o.cantidad_recibida for o in ordenes)
        total_optimo = sum(o.cantidad_entregada for o in ordenes)
        
        total_defectuoso = sum((o.cantidad_recibida - o.cantidad_entregada) for o in ordenes if o.cantidad_entregada is not None and o.cantidad_entregada > 0)
        
        precio_unitario_promedio = 35000 
        total_dinero_producido = total_optimo * precio_unitario_promedio
        
        porcentaje_eficiencia = 100.0
        if total_recibido > 0:
            porcentaje_eficiencia = round((total_optimo / total_recibido) * 100, 1)

        return jsonify({
            "total_recibido": total_recibido,
            "total_optimo": total_optimo,
            "total_defectuoso": total_defectuoso,
            "eficiencia": porcentaje_eficiencia,
            "precio_unitario": precio_unitario_promedio,
            "total_monetario": total_dinero_producido
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500