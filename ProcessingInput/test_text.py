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
    print("Testing basic generation...")
    model = genai.GenerativeModel('gemini-3-flash-preview')
    response = model.generate_content("Hello, can you hear me?")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Generation failed: {e}")
