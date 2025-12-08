# app.py
from flask import Flask
from routes.auth import auth
from routes.admin import admin
from routes.main import main
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# register blueprints
app.register_blueprint(auth)
app.register_blueprint(admin, url_prefix="/api")
app.register_blueprint(main)

# Health check
@app.route("/health")
def health():
    return {"status":"ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
