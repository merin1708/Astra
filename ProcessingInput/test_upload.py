import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key or api_key == "your_api_key_here":
    print("API Key not found!")
    exit(1)

genai.configure(api_key=api_key)

try:
    print("Attempting to upload audio_file.mp3...")
    uploaded_file = genai.upload_file("audio_file.mp3")
    print(f"Upload successful: {uploaded_file.uri}")
    genai.delete_file(uploaded_file.name)
    print("File deleted.")
except Exception as e:
    print(f"Upload failed: {e}")
