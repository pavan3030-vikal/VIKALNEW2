from flask import Flask, jsonify
from flask_cors import CORS
import os
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["https://vikal-new-production.up.railway.app"], methods=["GET", "POST", "OPTIONS"])

# Connect to Railway MongoDB
mongo_uri = os.getenv("MONGO_URL")
if not mongo_uri:
    logger.error("MONGO_URL not set")
    raise ValueError("MONGO_URL environment variable is missing")

client = MongoClient(mongo_uri)
db = client["vikal"]
users = db["users"]
chat_history = db["chat_history"]

@app.route('/')
def home():
    return jsonify({"message": "API is running", "status": "ok"}), 200

@app.route('/test-mongo', methods=['GET'])
def test_mongo():
    try:
        client.server_info()  # Test connection
        return jsonify({"message": "MongoDB connected successfully"}), 200
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)