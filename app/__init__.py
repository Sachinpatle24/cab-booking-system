from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from app.config import Config
from app.database.db_connection import get_db_connection
from app.routes.auth_routes import auth_bp
from app.routes.ride_routes import ride_bp
from app.routes.driver_routes import driver_bp
from app.routes.user_routes import user_bp
from app.routes.payment_routes import payment_bp
from app.routes.admin_routes import admin_bp
from app.routes.rating_routes import rating_bp
from app.utils.logger import setup_logger

jwt = JWTManager()
logger = setup_logger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    jwt.init_app(app)
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Cab Booking API",
            "description": "API for cab booking system with eco-friendly features",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter your JWT token in the format: Bearer <token>"
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)

    with app.app_context():
        conn = get_db_connection()
        if conn:
            logger.info("Database connected successfully")
            conn.close()
        else:
            logger.error("Database connection failed")

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ride_bp, url_prefix="/api/rides")
    app.register_blueprint(driver_bp, url_prefix="/api/drivers")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(payment_bp, url_prefix="/api/payments")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(rating_bp, url_prefix="/api/ratings")

    @app.route("/")
    def home():
        return {"message": "Cab Booking Backend Running", "status": "ok"}

    @app.route("/health")
    def health():
        return {"status": "healthy"}, 200

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {e}")
        return {"error": "Internal server error"}, 500

    return app
