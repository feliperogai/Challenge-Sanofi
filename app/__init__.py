from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import pymysql

# Instale PyMySQL como substituto para MySQLdb
pymysql.install_as_MySQLdb()

# Inicialize a instância do SQLAlchemy, Flask-Migrate e Flask-Mail
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app(config_class='config.Config'):
    app = Flask(__name__, instance_relative_config=True)

    # Carregar configurações
    app.config.from_object(config_class)  # Configuração padrão
    app.config.from_pyfile('config.py', silent=True)  # Configuração da instância (se existir)

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Configurar rotas
    with app.app_context():
        from .routes import configure_routes
        configure_routes(app)

    return app
