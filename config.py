import os
from dotenv import load_dotenv

SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
db_path = os.path.abspath('buildup.db')
DATABASE_URL = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'

class Config:
    SECRET_KEY = SECRET_KEY
    DATABASE_URL = DATABASE_URL
    REDIS_URL = REDIS_URL
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    DEMO_MODE = False  # Disable demo mode for real OTP
