import os
import flask
import json
import subprocess
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

# Gemini Service is initialized dynamically per-request to ensure fresh .env variables


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/batch_dashboard')
def batch_dashboard():
    return render_template('batch_dashboard.html')

@app.route('/api/batch_list')
def batch_list():
    import glob
    # Find all individual summary files in output dir
    files = glob.glob(os.path.join(OUTPUT_FOLDER, 'summary_*.json'))
    # Extract just the basenames
    filenames = [os.path.basename(f) for f in files]
    return jsonify({"files": filenames})

@app.route('/output/<path:filename>')
def serve_output(filename):
    return flask.send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        gemini_service = GeminiService()
    except Exception as e:
        return jsonify({"error": f"Gemini Service configuration error: {str(e)}"}), 500

    # 1. Check if it's raw text submitted
    if 'text_data' in request.form and request.form['text_data'].strip():
        text_content = request.form['text_data']
        return process_analysis(text_content, gemini_service, is_text=True)

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
            return process_analysis(text_content, gemini_service, is_text=True)
        else:
            return process_analysis(file_path, gemini_service, is_text=False)
            
    return jsonify({"error": "Invalid file type. Allowed: mp3, wav, txt, etc."}), 400


def process_analysis(data, gemini_service, is_text=False):
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
             
        # Trigger Ardra Automated Pipeline
        print("\n--- Triggering Ardra Automated Pipeline from Web App ---")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ardra_dir = os.path.join(base_dir, 'ardra')
        pipeline_script = os.path.join(ardra_dir, 'automated_pipeline.py')

        if os.path.exists(pipeline_script):
            try:
                subprocess.run(["python", "automated_pipeline.py"], cwd=ardra_dir, check=True)
                
                # Copy audit results to frontend output folder
                import shutil
                ardra_output = os.path.join(ardra_dir, 'output', 'audit_results.json')
                if os.path.exists(ardra_output):
                    shutil.copy(ardra_output, os.path.join(OUTPUT_FOLDER, 'audit_results.json'))
                print(f"Ardra pipeline completed! Audit results saved.")
            except subprocess.CalledProcessError as e:
                print(f"Error: Ardra pipeline failed with exit code {e.returncode}")
        else:
            print(f"Error: Could not find ardra pipeline script at {pipeline_script}")
             
        # Return success back to UI
        return jsonify({
            "success": True, 
            "message": "Analysis & Audit completed successfully",
            "data": result 
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8000)
