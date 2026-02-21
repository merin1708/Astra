import os
from dotenv import load_dotenv

class Config:
    MODEL_NAME = "gemini-3-flash-preview"

    @staticmethod
    def get_api_key():
        # Force load the .env file from the ProcessingInput directory inside the getter
        # so it bypasses Python's module-level cache entirely
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        load_dotenv(dotenv_path=env_path, override=True)
        return os.environ.get("GEMINI_API_KEY")

    @staticmethod
    def validate():
        api_key = Config.get_api_key()
        if not api_key or api_key == "your_api_key_here":
            raise ValueError("GEMINI_API_KEY environment variable not set in .env file.")
