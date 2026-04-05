import os
from dotenv import load_dotenv
load_dotenv()

class DevelopmentConfig:
    SECRET_KEY = 'smartattendance2024xK9mP'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Shaikh%402006@localhost:3306/smart_attendance'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}