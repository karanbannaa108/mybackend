import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not set")

client = MongoClient(MONGO_URI)

# extract DB name from URI
db_name = MONGO_URI.rsplit("/", 1)[-1].split("?")[0]

if not db_name:
    raise Exception("Database name missing in MONGO_URI")

db = client[db_name]

users_col = db["users"]
