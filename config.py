class Config:
    SECRET_KEY = 'decode_auth_token'
    SESSION_COOKIE_NAME = 'session_cookie'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:sanofi12345@database-sanofi.ctg4cskwkes6.us-east-1.rds.amazonaws.com/sistema_login'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'apenasenviando@gmail.com'
    MAIL_PASSWORD = 'muowtocyzjargwmm'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
