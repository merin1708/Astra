import os
import flask
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from src.services.gemini_service import GeminiService

app = Flask(__name__)

# Basic Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'txt', 'mp3', 'wav', 'm4a', 'ogg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB max-limit (for Gemini Inline Payload)

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize our AI Service
try:
    gemini_service = GeminiService()
except ValueError as e:
    print(f"Server Startup Error: {e}")
    gemini_service = None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/output/<path:filename>')
def serve_output(filename):
    return flask.send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if not gemini_service:
        return jsonify({"error": "Gemini Service not configured. Check API key."}), 500

    # 1. Check if it's raw text submitted
    if 'text_data' in request.form and request.form['text_data'].strip():
        text_content = request.form['text_data']
        return process_analysis(text_content, is_text=True)

    # 2. Otherwise expect a file
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        is_text_file = filename.lower().endswith('.txt')
        
        # Read the file if it's text, otherwise pass the path
        if is_text_file:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            # Clean up the .txt file, we have it in memory
            os.remove(file_path)
            return process_analysis(text_content, is_text=True)
        else:
            return process_analysis(file_path, is_text=False)
            
    return jsonify({"error": "Invalid file type. Allowed: mp3, wav, txt, etc."}), 400


def process_analysis(data, is_text=False):
    """ Helper to run the Gemini analysis and save outputs """
    try:
        if is_text:
            result = gemini_service.analyze_text(data)
        else:
            result = gemini_service.analyze_audio(data) # data = file_path here
            # Clean up audio upload after processing
            if os.path.exists(data):
                os.remove(data)
                
        if not result:
            return jsonify({"error": "Generative AI failed to process the request."}), 500

        # Save outputs
        output_file = os.path.join(OUTPUT_FOLDER, 'audio_analysis.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
            
        detailed_summary_data = {
            "detailed_summary": result.get("detailed_summary", {}),
            "agents_analysis": result.get("agents_analysis", []),
            "customer_analysis": result.get("customer_analysis", {})
        }
        summary_file = os.path.join(OUTPUT_FOLDER, 'detailed_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
             json.dump(detailed_summary_data, f, indent=4)
             
        # Return success back to UI
        return jsonify({
            "success": True, 
            "message": "Analysis completed successfully",
            "data": result 
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8000)
