from flask import Blueprint, jsonify, request
from functools import wraps
import jwt
import os

main_blueprint = Blueprint("main", __name__)
SECRET = os.environ.get("SECRET_KEY", "change_this_secret")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error":"Missing token"}), 401
        token = auth.split(" ",1)[1]
        try:
            jwt.decode(token, SECRET, algorithms=["HS256"])
        except Exception as e:
            return jsonify({"error":"Invalid token", "details": str(e)}), 401
        return f(*args, **kwargs)
    return decorated

@main_blueprint.route("/data")
def data():
    return jsonify({"msg":"This is your FREE API response!"})

@main_blueprint.route("/private")
@require_auth
def private():
    return jsonify({"msg":"Protected data — token ok"})
