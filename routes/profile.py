from flask import Blueprint, request, jsonify
from database.db import users_col
import jwt, os

profile = Blueprint("profile", __name__)
SECRET = os.environ.get("SECRET_KEY", "changeme")

def decode(auth):
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload["user"]
    except:
        return None

@profile.route("/profile", methods=["GET"])
def get_profile():
    username = decode(request.headers.get("Authorization"))
    if not username:
        return jsonify({"error": "Missing token"}), 401

    u = users_col.find_one({"username": username}, {"password": 0})
    return jsonify(u)


@profile.route("/profile", methods=["PUT"])
def update_profile():
    username = decode(request.headers.get("Authorization"))
    if not username:
        return jsonify({"error": "Missing token"}), 401

    updates = {}
    body = request.json
    for key in ["name", "bio", "avatar"]:
        if key in body:
            updates[f"profile.{key}"] = body[key]

    users_col.update_one({"username": username}, {"$set": updates})
    return jsonify({"msg": "Profile updated!"})
