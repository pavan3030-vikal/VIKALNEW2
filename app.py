from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
import re
from prompts import get_prompt
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Updated CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": ["https://vikal-new-production.up.railway.app", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "support_credentials": False
    }
})

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

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not set")
    raise ValueError("OPENAI_API_KEY environment variable is required")
logger.info("OpenAI API configured successfully")

def call_openai(prompt, max_tokens=700, model="gpt-4"):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    try:
        logger.info(f"Sending request to OpenAI with model {model}")
        response = requests.post(OPENAI_API_URL, json=payload, headers=headers)
        logger.info(f"OpenAI response status: {response.status_code}")
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        error_msg = f"OpenAI API error: {e} - Response: {e.response.text if e.response else 'No response'}"
        logger.error(error_msg)
        raise Exception(error_msg)

def update_stats(user_id, endpoint_type, question=None, response=None, category=None, style=None):
    logger.info(f"Inserting into chat_history for user {user_id}: {endpoint_type}")
    chat_history.insert_one({
        "user_id": user_id,
        "endpoint": endpoint_type,
        "question": question,
        "response": response,
        "category": category,
        "style": style,
        "timestamp": datetime.utcnow()
    })

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
        logger.info("Handling OPTIONS preflight for /explain")
        return jsonify({"status": "ok"}), 200
    data = request.get_json()
    if not data or 'topic' not in data:
        logger.error("No topic provided in request")
        return jsonify({'error': 'No topic provided'}), 400

    user_id = data.get('user_id', 'anonymous')
    topic = data['topic']
    style = data.get('explanation_style', 'teacher')
    category = data.get('category', 'generic')
    logger.info(f"Processing: user_id={user_id}, topic={topic}, style={style}, category={category}")
    return process_request(user_id, "explain", get_prompt(category, "explanation", style, topic), 700, topic, category, style, parse_explain_response)

@app.route('/solve', methods=['POST', 'OPTIONS'])
def solve():
    if request.method == "OPTIONS":
        logger.info("Handling OPTIONS preflight for /solve")
        return jsonify({"status": "ok"}), 200
    data = request.get_json()
    if not data or 'problem' not in data:
        logger.error("No problem provided in request")
        return jsonify({'error': 'No problem provided'}), 400

    user_id = data.get('user_id', 'anonymous')
    subject = data.get('subject')
    exam = data.get('exam')
    style = data.get('explanation_style', 'teacher')
    category = exam if exam else subject
    if not category:
        logger.error("Subject or exam required")
        return jsonify({'error': 'Subject or exam required'}), 400

    logger.info(f"Processing: user_id={user_id}, problem={data['problem']}, style={style}, category={category}")
    max_tokens = {"smart": 75, "step": 150, "teacher": 150, "research": 225}.get(style.lower(), 150)
    return process_request(user_id, "solve", get_prompt(category, "solution", style, data['problem']), max_tokens, data['problem'], category, style, parse_solve_response)

@app.route('/summarize-youtube', methods=['POST', 'OPTIONS'])
def summarize_youtube():
    if request.method == "OPTIONS":
        logger.info("Handling OPTIONS preflight for /summarize-youtube")
        return jsonify({"status": "ok"}), 200
    data = request.get_json()
    video_url = data.get('videoUrl')
    user_id = data.get('user_id', 'anonymous')

    if not video_url:
        logger.error("No video URL provided")
        return jsonify({'error': 'No video URL provided'}), 400

    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', video_url)
    if not video_id_match:
        logger.error("Invalid YouTube video URL")
        return jsonify({'error': 'Invalid YouTube video URL'}), 400

    video_id = video_id_match.group(1)

    try:
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

        if not user["isPro"] and user["chatCount"] >= 3:
            logger.warning(f"User {user_id} hit chat limit")
            return jsonify({"error": "Chat limit reached. Upgrade to Pro for unlimited chats!"}), 403

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        if not transcript:
            logger.error(f"No transcript available for video ID: {video_id}")
            return jsonify({'error': 'No transcript available for this video'}), 400

        transcript_text = "\n".join([f"[{item['start']:.1f}s] {item['text']}" for item in transcript])
        prompt = f"""
Your output should use the following template:
### Summary
### Analogy
### Notes
- [Emoji] Bulletpoint
### Keywords
- Explanation
You have been tasked with creating a concise summary of a YouTube video using its transcription.
Make a summary of the transcript.
Additionally make a short complex analogy to give context and/or analogy from day-to-day life from the transcript.
Create 10 bullet points (each with an appropriate emoji) that summarize the key points or important moments from the video's transcription.
In addition to the bullet points, extract the most important keywords and any complex words not known to the average reader as well as any acronyms mentioned. For each keyword and complex word, provide an explanation and definition based on its occurrence in the transcription.
Please ensure that the summary, bullet points, and explanations fit within the 330-word limit, while still offering a comprehensive and clear understanding of the video's content. Use the text above: Video Title {video_id} {transcript_text}.
"""
        response = call_openai(prompt, max_tokens=700)
        parts = re.split(r'###\s', response)
        summary_part = next((part for part in parts if part.startswith("Summary")), "")
        analogy_part = next((part for part in parts if part.startswith("Analogy")), "")
        notes_part = next((part for part in parts if part.startswith("Notes")), "")
        keywords_part = next((part for part in parts if part.startswith("Keywords")), "")

        summary = summary_part.replace("Summary", "").strip() if summary_part else ""
        analogy = analogy_part.replace("Analogy", "").strip() if analogy_part else ""
        notes = notes_part.replace("Notes", "").strip().split("\n")[:10] if notes_part else []
        keywords = keywords_part.replace("Keywords", "").strip().split("\n") if keywords_part else []

        combined_notes = f"{summary}\n\n**Analogy:** {analogy}\n\n**Key Points:**\n" + "\n".join(notes)
        flashcards = [f"{kw.split(' - ')[0]} - {kw.split(' - ')[1]}" for kw in keywords[:5] if " - " in kw]
        resources = [
            {"title": "YouTube Video", "url": video_url},
            {"title": "Wikipedia", "url": "https://en.wikipedia.org/wiki/YouTube"},
            {"title": "Khan Academy", "url": "https://www.khanacademy.org"}
        ]

        update_stats(user_id, "summarize-youtube", video_url, combined_notes)
        if not user["isPro"]:
            logger.info(f"Updating chat count for user {user_id}")
            users.update_one({"_id": user_id}, {"$inc": {"chatCount": 1}})

        logger.info("Returning YouTube summary response")
        return jsonify({"notes": combined_notes, "flashcards": flashcards, "resources": resources})
    except Exception as e:
        logger.error(f"Error summarizing YouTube video: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-youtube', methods=['POST', 'OPTIONS'])
def chat_youtube():
    if request.method == "OPTIONS":
        logger.info("Handling OPTIONS preflight for /chat-youtube")
        return jsonify({"status": "ok"}), 200
    data = request.get_json()
    video_id = data.get('video_id')
    user_query = data.get('query')
    user_id = data.get('user_id', 'anonymous')

    if not video_id or not user_query:
        logger.error("Missing video_id or query")
        return jsonify({'error': 'Missing video_id or query'}), 400

    try:
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

        if not user["isPro"] and user["chatCount"] >= 3:
            logger.warning(f"User {user_id} hit chat limit")
            return jsonify({"error": "Chat limit reached. Upgrade to Pro for unlimited chats!"}), 403

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        if not transcript:
            logger.error(f"No transcript available for video ID: {video_id}")
            return jsonify({'error': 'No transcript available for this video'}), 400

        transcript_text = "\n".join([f"[{item['start']:.1f}s] {item['text']}" for item in transcript])
        prompt = f"Based on this YouTube video transcript: {transcript_text}, answer the following question: {user_query}"
        response = call_openai(prompt, max_tokens=500)

        update_stats(user_id, "chat-youtube", user_query, response)
        if not user["isPro"]:
            logger.info(f"Updating chat count for user {user_id}")
            users.update_one({"_id": user_id}, {"$inc": {"chatCount": 1}})

        logger.info("Returning YouTube chat response")
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error chatting with YouTube video: {e}")
        return jsonify({'error': str(e)}), 500

def process_request(user_id, endpoint_type, prompt, max_tokens, question, category, style, parse_func):
    try:
        logger.info(f"Fetching user: {user_id}")
        user = users.find_one({"_id": user_id})
        if not user:
            logger.info(f"Creating new user: {user_id}")
            users.insert_one({
                "_id": user_id,
                "email": "unknown",
                "chatCount": 0,
                "isPro": False,
                "createdAt": datetime.utcnow()
            })
            user = users.find_one({"_id": user_id})
        if not user["isPro"] and user["chatCount"] >= 3:
            logger.warning(f"User {user_id} hit chat limit")
            return jsonify({"error": "Chat limit reached. Upgrade to Pro!"}), 403

        logger.info(f"Prompt: {prompt[:100]}...")
        response = call_openai(prompt, max_tokens)
        logger.info(f"OpenAI response: {response[:100]}...")
        parsed_response = parse_func(response)

        if not user["isPro"]:
            logger.info(f"Updating chat count for user {user_id}")
            users.update_one({"_id": user_id}, {"$inc": {"chatCount": 1}})
        update_stats(user_id, endpoint_type, question, parsed_response.get("notes"), category, style)

        logger.info("Returning response")
        return jsonify(parsed_response)
    except Exception as e:
        logger.error(f"Error in {endpoint_type} endpoint: {e}")
        return jsonify({'error': str(e)}), 500

def parse_explain_response(response):
    parts = re.split(r'###\s', response)
    parts = [part.strip() for part in parts if part.strip()]
    notes, points_to_remember, flashcards, resources = "", [], [], []
    for part in parts:
        if part.startswith("Quick Dive"):
            notes += part.replace("Quick Dive", "").strip() + "\n\n"
        elif part.startswith("Deep Dive"):
            notes += "**Deep Dive**\n" + part.replace("Deep Dive", "").strip() + "\n\n"
        elif part.startswith("Must-Knows"):
            notes += "**Must-Knows**\n" + part.replace("Must-Knows", "").strip() + "\n\n"
        elif part.startswith("VIKAL Brain Booster"):
            notes += "**VIKAL Brain Booster**\n" + part.replace("VIKAL Brain Booster", "").strip() + "\n\n"
        elif part.startswith("Real-World Wins"):
            notes += "**Real-World Wins**\n" + part.replace("Real-World Wins", "").strip() + "\n\n"
        elif part.startswith("VIKAL’s Exam Cheat Codes"):
            points_to_remember = part.replace("VIKAL’s Exam Cheat Codes", "").strip().split("\n")
            points_to_remember = [p.strip() for p in points_to_remember if p.strip()]
        elif part.startswith("Flashcards"):
            flashcards_raw = part.replace("Flashcards", "").strip().split("\n")
            for f in flashcards_raw:
                if "Q:" in f and "A:" in f:
                    q, a = f.split("A:", 1)
                    flashcards.append({"question": q.replace("Q:", "").strip(), "answer": a.strip()})
        elif part.startswith("Power-Ups"):
            resources = part.replace("Power-Ups", "").strip().split("\n")[:3]
            resources = [{"title": r.split(": ")[0].strip(), "url": r.split(": ")[1].strip() if ": " in r else r.strip()} for r in resources if r.strip()]
    return {"notes": notes, "points_to_remember": points_to_remember, "flashcards": flashcards, "resources": resources}

def parse_solve_response(response):
    parts = re.split(r'###\s', response)
    parts = [part.strip() for part in parts if part.strip()]
    notes, points_to_remember, resources = "", [], []
    for part in parts:
        if part.startswith("Solution"):
            notes = part.replace("Solution", "").strip()
        elif part.startswith("VIKAL’s Solve Smarter Hacks"):
            points_to_remember = part.replace("VIKAL’s Solve Smarter Hacks", "").strip().split("\n")
            points_to_remember = [p.strip() for p in points_to_remember if p.strip()]
        elif part.startswith("Power-Ups"):
            resources = part.replace("Power-Ups", "").strip().split("\n")[:5]
            resources = [{"title": r.split(": ")[0].strip(), "url": r.split(": ")[1].strip() if ": " in r else r.strip()} for r in resources if r.strip()]
    return {"notes": notes, "points_to_remember": points_to_remember, "flashcards": [], "resources": resources}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
