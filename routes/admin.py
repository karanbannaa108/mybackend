from flask import Blueprint, request, jsonify
import jwt, os
from database.db import users_col

admin = Blueprint("admin", __name__)
SECRET = os.environ.get("SECRET_KEY", "changeme")

def is_admin(auth):
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        if payload["role"] == "admin":
            return True
    except:
        return False
    return False

@admin.route("/admin/users", methods=["GET"])
def all_users():
    if not is_admin(request.headers.get("Authorization")):
        return jsonify({"error": "Admin required"}), 403

    users = list(users_col.find({}, {"password": 0, "refresh_tokens": 0}))
    return jsonify({"users": users})
