import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_secreta_sies_yullita'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:79604257@localhost/yullita_creaciones_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False