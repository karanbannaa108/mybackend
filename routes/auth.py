# routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from database.db import users_col
from passlib.hash import bcrypt
import jwt, os, datetime
from functools import wraps

auth = Blueprint("auth", __name__)

SECRET = os.environ.get("SECRET_KEY", "changeme")
ACCESS_EXPIRES_MIN = int(os.environ.get("ACCESS_EXPIRES_MIN", "15"))
REFRESH_EXPIRES_DAYS = int(os.environ.get("REFRESH_EXPIRES_DAYS", "7"))

def create_access_token(payload):
    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_EXPIRES_MIN)
    payload.update({"exp": exp, "type": "access"})
    return jwt.encode(payload, SECRET, algorithm="HS256")

def create_refresh_token(payload):
    exp = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_EXPIRES_DAYS)
    payload.update({"exp": exp, "type": "refresh"})
    return jwt.encode(payload, SECRET, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error":"Missing token"}), 401
        token = auth_header.split(" ",1)[1]
        try:
            data = jwt.decode(token, SECRET, algorithms=["HS256"])
            if data.get("type") != "access":
                raise jwt.InvalidTokenError("Wrong token type")
            request.user = data
        except Exception as e:
            return jsonify({"error":"Invalid token", "msg": str(e)}), 401
        return f(*args, **kwargs)
    return wrapper

@auth.route("/auth/register", methods=["POST"])
def register():
    body = request.get_json(force=True)
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return jsonify({"error":"username & password required"}), 400
    hashed = bcrypt.hash(password)
    user_doc = {"username": username, "password": hashed, "role": "user", "refresh_tokens": []}
    try:
        users_col.insert_one(user_doc)
    except Exception as e:
        return jsonify({"error":"User exists or DB error", "msg": str(e)}), 400
    return jsonify({"msg":"User registered (FREE)"}), 201

@auth.route("/auth/login", methods=["POST"])
def login():
    body = request.get_json(force=True)
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return jsonify({"error":"username & password required"}), 400
    user = users_col.find_one({"username": username})
    if not user or not bcrypt.verify(password, user["password"]):
        return jsonify({"error":"Invalid credentials"}), 401
    # create tokens
    payload = {"username": username, "role": user.get("role","user")}
    access = create_access_token(payload.copy())
    refresh = create_refresh_token(payload.copy())
    # store refresh token id (store full token or jti)
    users_col.update_one({"username": username}, {"$push": {"refresh_tokens": refresh}})
    return jsonify({"access_token": access, "refresh_token": refresh}), 200

@auth.route("/auth/refresh", methods=["POST"])
def refresh():
    body = request.get_json(force=True)
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        return jsonify({"error":"Missing refresh_token"}), 400
    try:
        data = jwt.decode(refresh_token, SECRET, algorithms=["HS256"])
        if data.get("type") != "refresh":
            raise jwt.InvalidTokenError("Wrong token type")
    except Exception as e:
        return jsonify({"error":"Invalid refresh token", "msg": str(e)}), 401
    username = data.get("username")
    user = users_col.find_one({"username": username})
    if not user or refresh_token not in user.get("refresh_tokens", []):
        return jsonify({"error":"Refresh token revoked"}), 401
    new_access = create_access_token({"username": username, "role": user.get("role","user")})
    return jsonify({"access_token": new_access}), 200

@auth.route("/auth/logout", methods=["POST"])
@token_required
def logout():
    body = request.get_json(force=True) or {}
    # optional: revoke refresh token
    refresh_token = body.get("refresh_token")
    username = request.user.get("username")
    if refresh_token:
        users_col.update_one({"username": username}, {"$pull": {"refresh_tokens": refresh_token}})
    return jsonify({"msg":"logged out"}), 200
