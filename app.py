from flask import Flask, render_template, request, redirect, url_for, session
import google.generativeai as genai
import os
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

app = Flask(__name__)
app.secret_key = os.getenv("FLASKSECRETKEY")  # Set this in your .env file

# -------------------------------
# Dummy homepage just for example
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        topic = request.form.get("topic")

        # Call Gemini to generate objectives for the topic
        prompt = f"Generate 3 to 5 clear and measurable learning objectives for a lesson on: {topic}"
        response = model.generate_content(prompt)

        # Process Gemini response into a clean list
        raw_objectives = response.text.strip().split("\n")
        cleaned_objectives = [line.lstrip("-•0123456789. ").strip() for line in raw_objectives if line.strip()]

        session["objectives"] = cleaned_objectives
        return redirect(url_for("review"))

    return render_template("home.html")

# -------------------------------
# Review page to view and refine objectives using an AI prompt
@app.route("/review", methods=["GET"])
def review():
    objectives = session.get("objectives", [])
    return render_template("review.html", objectives=objectives)

# -------------------------------
# Handles AI refinement based on teacher instruction
@app.route("/refine_objectives", methods=["POST"])
def refine_objectives():
    instruction = request.form.get("instruction")
    old_objectives = session.get("objectives", [])

    # Compose prompt for Gemini
    full_prompt = (
        "Here are some learning objectives:\n" +
        "\n".join(f"- {obj}" for obj in old_objectives) +
        f"\n\nBased on this instruction: '{instruction}', rewrite or modify the objectives."
    )

    # AI response
    response = model.generate_content(full_prompt)
    new_objectives = response.text.strip().split("\n")

    # Clean up
    cleaned = [obj.lstrip("-•0123456789. ").strip() for obj in new_objectives if obj.strip()]
    session["objectives"] = cleaned

    return redirect(url_for("review"))

# Route: start the tutor session (placeholder)
@app.route('/tutor/<token>')
def tutor(token):
    try:
        # Decrypt the token
        data = serializer.loads(token)
        topic = data['topic']
        return render_template('tutor.html', topic=topic)
    except Exception as e:
        return f"Invalid or expired token: {e}"

# Run app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000)) # Get port from environment, default to 5000
    app.run(host='0.0.0.0', port=port, debug=True) # debug=True is okay for dev, but set to False for production
