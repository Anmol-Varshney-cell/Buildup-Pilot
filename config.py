import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///buildup.db'
