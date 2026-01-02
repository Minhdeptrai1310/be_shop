from dotenv import load_dotenv
import os

load_dotenv(".env.dev")

print("Loading global configurations from .env file")
print("DB_URI:", os.environ.get("DB_URI"))
print("DB_NAME:", os.environ.get("DB_NAME"))
DB_URI = os.environ.get("DB_URI")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
APP_NAME = os.environ.get("APP_NAME")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
APP_PASSWORD = os.environ.get("APP_PASSWORD")


