from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql

# Instale PyMySQL como substituto para MySQLdb
pymysql.install_as_MySQLdb()

# Inicialize a instância do SQLAlchemy e Flask-Migrate
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Carregar configurações
    app.config.from_object('config.Config')  # Configuração padrão
    app.config.from_pyfile('config.py', silent=True)  # Configuração da instância (se existir)

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # Configurar rotas
    from .routes import configure_routes
    configure_routes(app)

    return app
