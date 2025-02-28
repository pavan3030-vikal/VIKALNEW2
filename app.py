from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
import re
from prompts import get_prompt  # Importing from prompts.py
from pymongo import MongoClient
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enhanced CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": "https://vikal-new-production.up.railway.app",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Railway MongoDB
mongo_uri = os.getenv("MONGO_URL")
if not mongo_uri:
    logger.error("MONGO_URL not set")
    raise ValueError("MONGO_URL environment variable is missing")
client = MongoClient(mongo_uri)
db = client["vikal"]
chat_history = db["chat_history"]
exam_dates = db["exam_dates"]
users = db["users"]

# OpenAI Configuration (Hardcoded Key)
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = "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"

def call_openai(prompt, max_tokens=700, model="gpt-3.5-turbo"):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(OPENAI_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logger.error(f"OpenAI API error: {e}")
        raise Exception(f"Failed to generate response: {e}")

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

@app.route('/explain', methods=['POST', 'OPTIONS'])
def explain():
    if request.method == "OPTIONS":
        # Handle preflight request manually if needed
        return jsonify({"status": "ok"}), 200

    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({'error': 'No topic provided'}), 400

    user_id = data.get('user_id', 'anonymous')
    topic = data['topic']
    style = data.get('explanation_style', 'teacher')
    category = data.get('category', 'generic')

    try:
        user = users.find_one({"_id": user_id})
        if not user:
            users.insert_one({
                "_id": user_id,
                "email": data.get("email", "unknown"),
                "chatCount": 0,
                "isPro": False,
                "createdAt": datetime.utcnow()
            })
            user = users.find_one({"_id": user_id})

        if not user["isPro"] and user["chatCount"] >= 3:
            return jsonify({"error": "Chat limit reached. Upgrade to Pro for unlimited chats!"}), 403

        prompt = get_prompt(category, "explanation", style, topic)
        response = call_openai(prompt, max_tokens=700)

        parts = re.split(r'###\s', response)
        parts = [part.strip() for part in parts if part.strip()]

        notes = ""
        flashcards = []
        resources = []
        exam_tips = []

        for part in parts:
            if part.startswith("Simple Explanation"):
                notes += part.replace("Simple Explanation", "").strip() + "\n\n"
            elif part.startswith("In-Depth Explanation"):
                notes += "**In-Depth Explanation**\n" + part.replace("In-Depth Explanation", "").strip() + "\n\n"
            elif part.startswith("Key Concepts or Formulas"):
                notes += "**Key Concepts or Formulas**\n" + part.replace("Key Concepts or Formulas", "").strip() + "\n\n"
            elif part.startswith("Real-World Applications or Examples"):
                notes += "**Real-World Applications**\n" + part.replace("Real-World Applications or Examples", "").strip() + "\n\n"
            elif part.startswith("Flashcards"):
                flashcards = part.replace("Flashcards", "").strip().split("\n")[:5]
                flashcards = [f.strip() for f in flashcards if f.strip()]
            elif part.startswith("Exam Tips"):
                exam_tips = part.replace("Exam Tips", "").strip().split("\n")[:5]
                exam_tips = [t.strip() for t in exam_tips if t.strip()]
                notes += "**Exam Tips**\n" + "\n".join(exam_tips) + "\n\n"
            elif part.startswith("Resources"):
                resources = part.replace("Resources", "").strip().split("\n")[:3]
                resources = [{"title": r.split(" - ")[0].strip(), "url": r.split(" - ")[1].strip() if " - " in r else r.strip()} 
                            for r in resources if r.strip()]

        notes = notes.strip()

        if not user["isPro"]:
            users.update_one({"_id": user_id}, {"$inc": {"chatCount": 1}})

        chat_history.insert_one({
            "user_id": user_id,
            "question": topic,
            "response": notes,
            "category": category,
            "style": style,
            "timestamp": datetime.utcnow()
        })

        return jsonify({
            "notes": notes,
            "flashcards": flashcards,
            "resources": resources
        })
    except Exception as e:
        logger.error(f"Error in explain endpoint: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)