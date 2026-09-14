from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.database import db

from backend.routes.auth_routes import auth_bp
from backend.routes.insumos_routes import insumos_bp
from backend.routes.produccion import produccion_bp
from backend.routes.calidad import calidad_bp
from backend.routes.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(insumos_bp)
    app.register_blueprint(produccion_bp)
    app.register_blueprint(calidad_bp)
    app.register_blueprint(dashboard_bp)

    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"mensaje": "Servidor de Creaciones Yullita Corriendo con exito"})

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)