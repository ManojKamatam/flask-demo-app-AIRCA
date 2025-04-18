import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-insecure-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '5'))
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    MEMORY_LEAK_ENABLED = os.environ.get('MEMORY_LEAK_ENABLED', 'False') == 'True'
    SLOW_QUERY_ENABLED = os.environ.get('SLOW_QUERY_ENABLED', 'False') == 'True'