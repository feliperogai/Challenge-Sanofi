class Config:
    SECRET_KEY = 'decode_auth_token'
    SESSION_COOKIE_NAME = 'session_cookie'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:sanofi12345@database-sanofi.ctg4cskwkes6.us-east-1.rds.amazonaws.com/sistema_login'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = '98c6e73dbaf6f1'
    MAIL_PASSWORD = '1a426a165b2c41'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
