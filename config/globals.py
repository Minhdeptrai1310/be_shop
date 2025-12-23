from dotenv import load_dotenv
import os

load_dotenv()

# print("Loading global configurations from .env file")
# print("DB_URI:", os.environ.get("DB_URI"))
# print("DB_NAME:", os.environ.get("DB_NAME"))
DB_URI = "mongodb://localhost:27017/"
DB_NAME = "shop_db"


