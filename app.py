from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
import re
from prompts import get_prompt
from pymongo import MongoClient
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "https://vikal-new-production.up.railway.app",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# MongoDB
mongo_uri = os.getenv("MONGO_URL")
if not mongo_uri:
    logger.error("MONGO_URL not set")
    raise ValueError("MONGO_URL environment variable is missing")
client = MongoClient(mongo_uri)
db = client["vikal"]
chat_history = db["chat_history"]
exam_dates = db["exam_dates"]
users = db["users"]
logger.info("MongoDB connected successfully")

# OpenAI with Placeholder
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = "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"  # Replace with real key later
logger.info(f"Using OpenAI API Key: {OPENAI_API_KEY[:5]}...")

def call_openai(prompt, max_tokens=700, model="gpt-3.5-turbo"):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    try:
        logger.info(f"Sending request to OpenAI: {payload}")
        response = requests.post(OPENAI_API_URL, json=payload, headers=headers)
        logger.info(f"OpenAI response status: {response.status_code}")
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logger.error(f"OpenAI API error: {e} - Response: {e.response.text if e.response else 'No response'}")
        raise Exception(f"Failed to generate response: {e}")

@app.route('/')
def home():
    return jsonify({"message": "API is running", "status": "ok"}), 200

@app.route('/test-mongo', methods=['GET'])
def test_mongo():
    try:
        client.server_info()
        return jsonify({"message": "MongoDB connected successfully"}), 200
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/explain', methods=['POST', 'OPTIONS'])
def explain():
    if request.method == "OPTIONS":
        logger.info("Handling OPTIONS preflight")
        return jsonify({"status": "ok"}), 200

    data = request.get_json()
    logger.info(f"Received data: {data}")
    if not data or 'topic' not in data:
        logger.error("No topic provided in request")
        return jsonify({'error': 'No topic provided'}), 400

    user_id = data.get('user_id', 'anonymous')
    topic = data['topic']
    style = data.get('explanation_style', 'teacher')
    category = data.get('category', 'generic')
    logger.info(f"Processing: user_id={user_id}, topic={topic}, style={style}, category={category}")

    try:
        logger.info(f"Fetching user: {user_id}")
        user = users.find_one({"_id": user_id})
        if not user:
            logger.info(f"Creating new user: {user_id}")
            users.insert_one({
                "_id": user_id,
                "email": data.get("email", "unknown"),
                "chatCount": 0,
                "isPro": False,
                "createdAt": datetime.utcnow()
            })
            user = users.find_one({"_id": user_id})
        logger.info(f"User found: {user}")

        if not user["isPro"] and user["chatCount"] >= 3:
            logger.warning(f"User {user_id} hit chat limit")
            return jsonify({"error": "Chat limit reached. Upgrade to Pro for unlimited chats!"}), 403

        logger.info("Generating prompt")
        prompt = get_prompt(category, "explanation", style, topic)
        logger.info(f"Prompt: {prompt[:100]}...")  # Truncate for brevity
        response = call_openai(prompt, max_tokens=700)
        logger.info(f"OpenAI response: {response[:100]}...")

        parts = re.split(r'###\s', response)
        parts = [part.strip() for part in parts if part.strip()]
        logger.info(f"Response parts: {len(parts)}")

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
        logger.info(f"Parsed: notes={len(notes)}, flashcards={len(flashcards)}, resources={len(resources)}")

        if not user["isPro"]:
            logger.info(f"Updating chat count for user {user_id}")
            users.update_one({"_id": user_id}, {"$inc": {"chatCount": 1}})

        logger.info(f"Inserting into chat_history: {topic}")
        chat_history.insert_one({
            "user_id": user_id,
            "question": topic,
            "response": notes,
            "category": category,
            "style": style,
            "timestamp": datetime.utcnow()
        })

        logger.info("Returning response")
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
