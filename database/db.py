from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["production"]
users_col = db["users"]
