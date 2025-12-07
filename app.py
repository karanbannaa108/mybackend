from flask import Flask, jsonify
from flask_cors import CORS
import os

# Blueprints
from routes.auth import auth_blueprint
from routes.main import main_blueprint

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(main_blueprint, url_prefix="/api")

@app.route("/")
def home():
    return jsonify({"msg": "FREE Python Backend Server Live!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
