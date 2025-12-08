# database/db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/mydb")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client.get_default_database() if client.get_default_database() else client["mydb"]

users_col = db["users"]
# Example index: ensure username unique
users_col.create_index("username", unique=True, background=True)
