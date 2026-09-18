import os

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from google.genai import types

from chatbot_config import CHATBOT_PROMPT

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in the .env file.")

client = genai.Client(api_key=API_KEY)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a study question."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=CHATBOT_PROMPT,
                temperature=0.3,
            ),
        )

        answer = response.text or "I couldn't generate an answer. Please try again."
        return jsonify({"answer": answer})

    except Exception as exc:
        app.logger.exception("Gemini API request failed")
        return jsonify({
            "error": "The study assistant is temporarily unavailable."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
