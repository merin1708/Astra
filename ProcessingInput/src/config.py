import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    MODEL_NAME = "gemini-3-flash-preview"

    @staticmethod
    def validate():
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == "your_api_key_here":
            raise ValueError("GEMINI_API_KEY environment variable not set in .env file.")
