import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'decode_auth_token'
    SESSION_COOKIE_NAME = 'session_cookie'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://admin:sanofi12345@database-sanofi.ctg4cskwkes6.us-east-1.rds.amazonaws.com/sistema_login'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 2525)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '98c6e73dbaf6f1'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '1a426a165b2c41'
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') == 'True'
