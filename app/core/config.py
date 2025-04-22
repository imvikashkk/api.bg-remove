# app/core/config.py
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 180)) # 3 hour
JWT_EXPIRE_MINUTES_REMEMBER = int(os.getenv("JWT_EXPIRE_MINUTES_REMEMBER", 21600)) # 15 Days
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_EMAIL_SEND_AS = os.getenv("SMTP_EMAIL_SEND_AS")
SMTP_EMAIL_PASS = os.getenv("SMTP_EMAIL_PASS")
PRODUCTION = bool(os.getenv("PRODUCTION")) | False
