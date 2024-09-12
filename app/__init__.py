from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Carregar configurações
    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # Configurar rotas
    from .routes import configure_routes
    configure_routes(app)

    return app
