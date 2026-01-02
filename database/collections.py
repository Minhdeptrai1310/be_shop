from enum import Enum
from urllib.parse import quote_plus
from fastapi import Depends
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config.globals import DB_URI, DB_NAME, DB_USER, DB_PASSWORD, APP_NAME


class Collections(Enum):
    USERS = "users"
    CATEGORIES = "categories"
    ROLES = "roles"
    PRODUCTS = "products"
    UPLOADS = "uploads"
    MAILS = "mails"
    CARTS = "carts"
    ORDERS = "orders"
    ORDER_ITEMS = "order_items"


def init_db():
    user = quote_plus(DB_USER)
    password = quote_plus(DB_PASSWORD)
    uri = f"mongodb+srv://{user}:{password}@{DB_URI}/?appName={APP_NAME}"
    mongo_client = MongoClient(uri)
    try:
        mongo_client.admin.command('ping')
        print("Connected to MongoDB")
    except PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}")
        raise e
    db = mongo_client[DB_NAME]
    try:
        db.command('ping')
        print("Connected to MongoDB database")
    except PyMongoError as e:
        print(f"Error connecting to MongoDB database: {e}")
        raise e
    return db


def get_user_collection(db=Depends(init_db)):
    return db[Collections.USERS.value]


def get_category_collection(db=Depends(init_db)):
    return db[Collections.CATEGORIES.value]


def get_role_collection(db=Depends(init_db)):
    return db[Collections.ROLES.value]


def get_product_collection(db=Depends(init_db)):
    return db[Collections.PRODUCTS.value]

def get_upload_collection(db=Depends(init_db)):
    return db[Collections.UPLOADS.value]

def get_mail_collection(db=Depends(init_db)):
    return db[Collections.MAILS.value]

def get_cart_collection(db=Depends(init_db)):
    return db[Collections.CARTS.value]

def get_order_collection(db=Depends(init_db)):
    return db[Collections.ORDERS.value]

def get_order_items_collection(db=Depends(init_db)):
    return db[Collections.ORDER_ITEMS.value]

