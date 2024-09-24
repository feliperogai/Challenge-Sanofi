from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=False, default='user')

class Treinamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_treinamento = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    link = db.Column(db.String(200), nullable=True)
    presenca_confirmada = db.Column(db.Boolean, default=False)

class UsuarioTreinamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    treinamento_id = db.Column(db.Integer, db.ForeignKey('treinamento.id'), nullable=False)
    presenca_confirmada = db.Column(db.Boolean, default=False)
