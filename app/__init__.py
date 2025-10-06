from flask import Flask
from flask_cors import CORS
from config import Config


# This file creates and configures the Flask application.
# It uses the "application factory" pattern. like a function that builds
# and returns the app instance.
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app)
    
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app