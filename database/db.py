from pymongo import MongoClient
import os

# Use environment variable for security
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not set")

client = MongoClient(MONGO_URI)
db = client["free_backend"]
users_col = db["users"]
