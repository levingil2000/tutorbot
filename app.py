from flask import Flask, render_template, request, redirect, url_for, session
import google.generativeai as genai
import os
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer

# Load environment variables from .env file
load_dotenv()

# Configure your secret keys
FLASK_SECRET_KEY = os.getenv("FLASKSECRETKEY", "fallback-secret-key")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup OpenAI API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

# Setup itsdangerous serializer for secure token generation
serializer = URLSafeSerializer(app.config['SECRET_KEY'])

# Helper function to ask Gemini to generate objectives based on topic
def generate_objectives(topic):
    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel("gemini-pro")
        
        # Generate objectives
        response = model.generate_content(f"Generate 3-5 clear learning objectives for a lesson about '{topic}'.")

        return response.text
    except Exception as e:
        return f"Error: {e}"

# Route: home page for entering a topic
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        topic = request.form['topic']
        # Generate objectives from Gemini
        objectives = generate_objectives(topic)

        # Save data into session
        session['topic'] = topic
        session['objectives'] = objectives

        # Create a secure token to access the tutor session
        token = serializer.dumps({'topic': topic})
        session['token'] = token

        return redirect(url_for('review'))
    return render_template('index.html')

# Route: review the AI-generated objectives
@app.route('/review')
def review():
    topic = session.get('topic')
    objectives = session.get('objectives')
    token = session.get('token')
    return render_template('review.html', topic=topic, objectives=objectives, token=token)

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
