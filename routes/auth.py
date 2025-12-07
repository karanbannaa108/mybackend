from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from database.db import users_col
import os

auth_blueprint = Blueprint("auth", __name__)
bcrypt = Bcrypt()
SECRET = os.environ.get("SECRET_KEY", "change_this_secret")

@auth_blueprint.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error":"username and password required"}), 400

    if users_col.find_one({"username": username}):
        return jsonify({"error":"username already exists"}), 400

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    users_col.insert_one({"username": username, "password": hashed})
    return jsonify({"msg":"User registered (FREE)"}), 201

@auth_blueprint.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error":"username and password required"}), 400

    user = users_col.find_one({"username": username})
    if not user:
        return jsonify({"error":"Invalid credentials"}), 401

    if bcrypt.check_password_hash(user["password"], password):
        token = jwt.encode(
            {"user": username, "exp": datetime.utcnow() + timedelta(days=1)},
            SECRET,
            algorithm="HS256"
        )
        return jsonify({"token": token})

    return jsonify({"error":"Invalid credentials"}), 401
