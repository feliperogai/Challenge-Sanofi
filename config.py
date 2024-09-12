class Config:
    SECRET_KEY = '010403'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:010403@localhost/sistema_login'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.example.com'  # Substitua pelo servidor SMTP que você usará
    MAIL_PORT = 587  # Substitua pela porta usada pelo servidor SMTP
    MAIL_USERNAME = 'your_email@example.com'  # Substitua pelo seu e-mail
    MAIL_PASSWORD = 'your_password'  # Substitua pela sua senha
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
