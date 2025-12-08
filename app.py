from flask import Flask, jsonify
from flask_cors import CORS
import os

from routes.auth import auth
from routes.profile import profile
from routes.admin import admin

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(profile, url_prefix="/")
app.register_blueprint(admin, url_prefix="/")

@app.route("/")
def home():
    return jsonify({"msg": "Backend Live — karanbannaa108"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
