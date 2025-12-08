from flask import Flask, jsonify, request
import jwt, os, time
from functools import wraps
from pymongo import MongoClient
from flask_cors import CORS

# ------------------------------------------
# CONFIG
# ------------------------------------------
SECRET = os.getenv("SECRET_KEY", "changeme")
MONGO_URI = os.getenv("MONGO_URI", "")
client = MongoClient(MONGO_URI)
db = client["mydb"]
users_col = db["users"]

app = Flask(__name__)
CORS(app)

# ------------------------------------------
# TOKEN GENERATOR
# ------------------------------------------
def create_token(username, role="user", exp=3600):
    payload = {
        "username": username,
        "role": role,
        "exp": time.time() + exp
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

# ------------------------------------------
# TOKEN VERIFY
# ------------------------------------------
def protected_route(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "No token found"}), 401

        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            request.user = payload["username"]
        except:
            return jsonify({"error": "Invalid / Expired token"}), 401

        return f(*args, **kwargs)
    return decorated

# ------------------------------------------
# REGISTER
# ------------------------------------------
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if users_col.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    users_col.insert_one({
        "username": username,
        "password": password,
        "refresh_tokens": 0,
        "role": "user"
    })

    return jsonify({"msg": "User registered"}), 201

# ------------------------------------------
# LOGIN
# ------------------------------------------
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users_col.find_one({"username": username, "password": password})
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_token(username, user.get("role", "user"), exp=3600)
    refresh_token = create_token(username, user.get("role", "user"), exp=86400)

    users_col.update_one(
        {"username": username},
        {"$set": {"refresh_tokens": refresh_token}}
    )

    return jsonify({
        "msg": "Login success",
        "access_token": access_token,
        "refresh_token": refresh_token
    })

# ------------------------------------------
# REFRESH TOKEN
# ------------------------------------------
@app.route("/auth/refresh", methods=["POST"])
def refresh_token():
    data = request.json
    refresh = data.get("refresh_token")

    if not refresh:
        return jsonify({"error": "No refresh token"}), 401

    user = users_col.find_one({"refresh_tokens": refresh})
    if not user:
        return jsonify({"error": "Invalid refresh token"}), 403

    try:
        decoded = jwt.decode(refresh, SECRET, algorithms=["HC256"])
    except:
        return jsonify({"error": "Expired refresh token"}), 403

    new_access = create_token(decoded["username"], decoded["role"], exp=3600)

    return jsonify({"access_token": new_access})

# ------------------------------------------
# PRIVATE API
# ------------------------------------------
@app.route("/api/private", methods=["GET"])
@protected_route
def private_api():
    return jsonify({
        "msg": "Protected route accessed",
        "user": request.user
    })

# ------------------------------------------
# ROOT CHECK
# ------------------------------------------
@app.route("/")
def home():
    return jsonify({"status": "API Working"})


# ------------------------------------------
# START APP
# ------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
