import os
from flask import Flask, render_template, request, jsonify
from google import genai
from dotenv import load_dotenv

# Load variables from your .env file
load_dotenv()

# Initialize Flask and Gemini Client
app = Flask(__name__)
client = genai.Client()

@app.route('/')
def home():
    # Looks for a folder named 'templates' and loads your index.html
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    # 1. Read message from multi-part Form Data instead of JSON
    user_message = request.form.get('message', '').strip()
    
    # Catch any uploaded file object (for your PDF features)
    uploaded_file = request.files.get('file')

    # If the user typed nothing but attached a file, provide a default prompt
    if not user_message and uploaded_file:
        user_message = "Please analyze this file."
    
    if not user_message:
        return jsonify({'reply': 'No message received'}), 400

    try:
        # 2. Generate a response using the correct Gemini model identifier
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
        )
        
        # 3. Return 'reply' to match what your index.html JavaScript expects
        return jsonify({'reply': response.text})
        
    except Exception as e:
        return jsonify({'reply': f"Error generating response: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
