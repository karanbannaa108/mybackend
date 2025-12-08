import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

# --- IMPORTANT FIX ---
# Always pick DB name from the URI
db = client.get_database()

# Collections
users_col = db["users"]
refresh_tokens_col = db["refresh_tokens"]
