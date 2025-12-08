from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt, secrets
from datetime import datetime, timedelta
from database.db import users_col
import os

auth = Blueprint("auth", __name__)
bcrypt = Bcrypt()

SECRET = os.environ.get("SECRET_KEY", "changeme")
ACCESS_EXPIRE_MIN = 10
REFRESH_EXPIRE_DAYS = 30

def create_access(user, role):
    return jwt.encode(
        {
            "user": user,
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MIN)
        },
        SECRET,
        algorithm="HS256",
    )

def create_refresh():
    return secrets.token_urlsafe(64)

@auth.route("/register", methods=["POST"])
def register():
    data = request.json
    user = data["username"]
    password = data["password"]

    if users_col.find_one({"username": user}):
        return jsonify({"error": "User exists"}), 400

    hashed = bcrypt.generate_password_hash(password).decode()
    users_col.insert_one({
        "username": user,
        "password": hashed,
        "role": "user",
        "profile": {},
        "refresh_tokens": []
    })

    return jsonify({"msg": "User registered!"}), 201


@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data["username"]
    password = data["password"]

    u = users_col.find_one({"username": user})
    if not u or not bcrypt.check_password_hash(u["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    access = create_access(user, u["role"])
    refresh = create_refresh()

    hashed_refresh = bcrypt.generate_password_hash(refresh).decode()
    users_col.update_one({"username": user}, {"$push": {"refresh_tokens": hashed_refresh}})

    return jsonify({"token": access, "refresh_token": refresh})


@auth.route("/refresh", methods=["POST"])
def refresh():
    data = request.json
    rt = data["refresh_token"]

    for u in users_col.find({}):
        for saved_hash in u["refresh_tokens"]:
            if bcrypt.check_password_hash(saved_hash, rt):
                new_access = create_access(u["username"], u["role"])
                return jsonify({"token": new_access})

    return jsonify({"error": "invalid"}), 400


@auth.route("/logout", methods=["POST"])
def logout():
    data = request.json
    rt = data["refresh_token"]

    for u in users_col.find({}):
        new_list = []
        removed = False
        for saved_hash in u["refresh_tokens"]:
            if bcrypt.check_password_hash(saved_hash, rt):
                removed = True
                continue
            new_list.append(saved_hash)

        if removed:
            users_col.update_one({"username": u["username"]}, {"$set": {"refresh_tokens": new_list}})
            return jsonify({"msg": "Logged out"})

    return jsonify({"error": "Invalid refresh token"}), 400
