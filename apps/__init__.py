# -*- encoding: utf-8 -*-
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module


db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


# def register_blueprints(app):
#     for module_name in ('authentication', 'home'):
#         module = import_module('apps.{}.routes'.format(module_name))
#         app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

from apps.authentication.oauth import github_blueprint

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)

    app.register_blueprint(github_blueprint, url_prefix="/login")
    
    register_blueprints(app)
    configure_database(app)
    
    # Move Arduino initialization here, after all blueprints are registered
    try:
        from apps.arduino.controller import init_arduino
        controller = init_arduino(port=app.config.get('ARDUINO_PORT', 'COM12'))
        app.logger.info(f"Arduino controller initialized: {controller is not None}")
    except Exception as e:
        app.logger.error(f"Error initializing Arduino controller: {str(e)}")
    
    return app

def register_blueprints(app):
    for module_name in ('authentication', 'home', 'arduino'):  # Añadir 'arduino'
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)