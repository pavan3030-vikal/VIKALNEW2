from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["https://vikal-new-production.up.railway.app"], methods=["GET", "POST", "OPTIONS"])

@app.route('/')
def home():
    return jsonify({"message": "API is running", "status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)