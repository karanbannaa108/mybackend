# routes/main.py
from flask import Blueprint, jsonify
main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    return jsonify({"msg":"API root. Use /auth/login, /auth/register, /api/*"}), 200
