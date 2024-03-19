import os

from dotenv import load_dotenv
load_dotenv()

# External API configuration
FUB_API = os.getenv('FUB_API')
X_SYSTEM_KEY = os.getenv('X_SYSTEM_KEY')
X_SYSTEM = os.getenv('X_SYSTEM')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SLACK_MAY_TOKEN = os.getenv('SLACK_MAY_TOKEN')

# Internal API configuration
FUB_TEXTING_SERVICE = os.getenv('FUB_TEXTING_SERVICE')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_NAME = DATABASE_URL.split('/')[-1]
DATABASE_USER = DATABASE_URL.split('/')[2].split(':')[0]
DATABASE_PASSWORD = DATABASE_URL.split('/')[2].split(':')[1].split('@')[0]
DATABASE_HOST = DATABASE_URL.split('@')[1].split(':')[0]
DATABASE_PORT = DATABASE_URL.split('@')[1].split(':')[1].split('/')[0]

# Celery configuration
CELERY_BROKER_URL = os.getenv('REDIS_URL')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL')