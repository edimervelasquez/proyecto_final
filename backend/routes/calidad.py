from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models.models import Produccion, ProgramacionUsuario

calidad_bp = Blueprint('calidad', __name__, url_prefix='/api/produccion/calidad')

@calidad_bp.route('', methods=['POST'])
def registrar_control_calidad():
    data = request.get_json()
    
    id_produccion = data.get('id_produccion')
    cantidad_optima = data.get('cantidad_optima')
    cantidad_defectuosa = data.get('cantidad_defectuosa')
    
    if id_produccion is None or cantidad_optima is None or cantidad_defectuosa is None:
        return jsonify({"error": "Datos incompletos. Se requiere id_produccion, cantidad_optima y cantidad_defectuosa."}), 400
        
    try:
        id_produccion = int(id_produccion)
        cantidad_optima = int(cantidad_optima)
        cantidad_defectuosa = int(cantidad_defectuosa)
        
        orden = Produccion.query.get(id_produccion)
        if not orden:
            return jsonify({"error": f"No se encontró ninguna orden de producción con el ID {id_produccion}."}), 404
            
        total_procesado = cantidad_optima + cantidad_defectuosa
        if total_procesado > orden.cantidad_recibida:
            return jsonify({
                "error": f"Inconsistencia: El lote recibió {orden.cantidad_recibida} unidades, intentas reportar {total_procesado}."
            }), 400
            
        orden.cantidad_entregada = cantidad_optima

        reporte_calidad = ProgramacionUsuario(
            id_programacion=1,
            id_rol=3,
            cantidad_recibida=orden.cantidad_recibida,
            cantidad_entregada=cantidad_optima,
            cantidad_defectuosa=cantidad_defectuosa
        )
        db.session.add(reporte_calidad)
        db.session.commit()
        
        return jsonify({
            "mensaje": f"¡Control de calidad para la Orden #{id_produccion} guardado exitosamente!",
            "unidades_aprobadas": cantidad_optima,
            "unidades_defectuosas": cantidad_defectuosa,
            "estado": "Lote cerrado y listo para distribución."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500