import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load variables from your .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './temp_uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the Gemini Client
client = genai.Client()

# Set up a smart document analyst persona configuration
analyst_config = types.GenerateContentConfig(
    system_instruction="""
    You are Verity, an elite academic assistant and document analyst. 
    When answering questions about uploaded files or general concepts, use clean markdown formatting.
    Use bold headers, bullet points for lists, and highlight critical formulas or technical steps cleanly.
    """,
    temperature=0.4,
)
chat = client.chats.create(model="gemini-2.0-flash", config=analyst_config)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_message = request.form.get('message', '').strip()
    uploaded_file = request.files.get('file')
    
    contents_payload = []

    # Handle PDF file processing
    if uploaded_file and uploaded_file.filename != '':
        try:
            filename = secure_filename(uploaded_file.filename)
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(local_path)
            
            print(f"Uploading {filename} to Gemini File Manager...")
            gemini_file = client.files.upload(file=local_path)
            contents_payload.append(gemini_file)
            
            os.remove(local_path)
        except Exception as e:
            return jsonify({'reply': f"❌ Error processing file: {str(e)}"})

    if user_message:
        contents_payload.append(user_message)

    if not contents_payload:
        return jsonify({'reply': "I didn't catch that. Please type a message or attach a file."})
    
    try:
        response = chat.send_message(contents_payload)
        return jsonify({'reply': response.text})
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return jsonify({
                'reply': "⚠️ **Quota Limit Reached:** Your free-tier Gemini API key has run out of requests for the moment. Please wait a bit or try again later!"
            })
        return jsonify({'reply': f"Error generating response: {error_msg}"})

if __name__ == '__main__':
    # Start the Flask server purely on localhost port 5000
    app.run(debug=True, port=5000)