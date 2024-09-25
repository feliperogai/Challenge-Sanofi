from. import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Nome da tabela no banco de dados
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    tipo_usuario = db.Column(db.Enum('admin', 'user'), nullable=False, default='user')

    # Relacionamento com UsuarioTreinamento
    treinamentos = db.relationship('UsuarioTreinamento', backref='usuario', lazy=True)

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    token = db.Column(db.String(255), primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Presenca(db.Model):
    __tablename__ = 'presenca'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    data_hora = db.Column(db.String(50), nullable=False)
    assinatura = db.Column(db.String(100), nullable=False)

class Treinamento(db.Model):
    __tablename__ = 'treinamentos'  # Nome da tabela no banco de dados
    id = db.Column(db.Integer, primary_key=True)
    nome_treinamento = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    link = db.Column(db.String(255), nullable=False)
    presenca_confirmada = db.Column(db.Boolean, default=False)

    # O backref aqui pode ser renomeado
    usuario_treinamentos = db.relationship('UsuarioTreinamento', backref='treinamento', lazy=True)

class UsuarioTreinamento(db.Model):
    __tablename__ = 'usuario_treinamento'  # Nome da tabela no banco de dados
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    treinamento_id = db.Column(db.Integer, db.ForeignKey('treinamentos.id'), nullable=False)

    # Removido o backref adicional
    # O relacionamento com Treinamento já é suficiente
    # Se quiser, você pode deixar apenas um backref único
