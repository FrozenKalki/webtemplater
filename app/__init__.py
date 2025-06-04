from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Initialize extensions

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_object='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    with app.app_context():
        from .views import auth, templates, dictionaries
        app.register_blueprint(auth.bp)
        app.register_blueprint(templates.bp)
        app.register_blueprint(dictionaries.bp)
        db.create_all()

    return app
