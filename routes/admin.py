# routes/admin.py
from flask import Blueprint, jsonify, request
import os, jwt
from database.db import users_col

admin = Blueprint("admin", __name__)
SECRET = os.environ.get("SECRET_KEY", "changeme")

def is_admin(auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ",1)[1]
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload.get("role") == "admin"
    except Exception:
        return False

@admin.route("/admin/users", methods=["GET"])
def all_users():
    if not is_admin(request.headers.get("Authorization")):
        return jsonify({"error":"Admin required"}), 403
    users = list(users_col.find({}, {"password":0, "refresh_tokens":0}))
    for u in users:
        u["_id"] = str(u["_id"])
    return jsonify({"users": users})
