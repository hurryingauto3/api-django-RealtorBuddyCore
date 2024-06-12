import os

from dotenv import load_dotenv

load_dotenv()

DEBUG_ = os.getenv("DEBUG")
ALLOWED_HOSTS_ = os.getenv("ALLOWED_HOSTS")

# External API configuration
FUB_API = os.getenv("FUB_API")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
TWILIO_ACCOUNT_SID_ = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN_ = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER_ = os.getenv("TWILIO_NUMBER")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PAYMENT_LINK = os.getenv("STRIPE_PAYMENT_LINK")
SLACK_BA_TOKEN = os.getenv("SLACK_BA_TOKEN")
G_CLIENT_ID = os.getenv("G_CLIENT_ID")
G_CLIENT_SECRET = os.getenv("G_CLIENT_SECRET")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_NAME = DATABASE_URL.split("/")[-1]
DATABASE_USER = DATABASE_URL.split("/")[2].split(":")[0]
DATABASE_PASSWORD = DATABASE_URL.split("/")[2].split(":")[1].split("@")[0]
DATABASE_HOST = DATABASE_URL.split("@")[1].split(":")[0]
DATABASE_PORT = DATABASE_URL.split("@")[1].split(":")[1].split("/")[0]

# Celery configuration
CELERY_BROKER_URL_ = os.getenv("REDIS_URL")
CELERY_RESULT_BACKEND_ = os.getenv("REDIS_URL")
