from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
import re
from prompts import get_prompt  # Importing from prompts.py

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["https://vikal-new-production.up.railway.app"], methods=["GET", "POST", "OPTIONS"])

# OpenAI Configuration
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not set")
    raise ValueError("OPENAI_API_KEY environment variable is missing")

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

@app.route('/explain', methods=['POST'])
def explain():
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({'error': 'No topic provided'}), 400

    topic = data['topic']
    style = data.get('explanation_style', 'teacher')  # Default to 'teacher'
    category = data.get('category', 'generic')       # Default to 'generic'

    try:
        # Get prompt from prompts.py
        prompt = get_prompt(category, "explanation", style, topic)
        response = call_openai(prompt, max_tokens=700)

        # Parse the response
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