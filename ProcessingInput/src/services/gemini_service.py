import json
from google import genai
from google.genai import types
from src.config import Config

class GeminiService:
    def __init__(self):
        Config.validate()
        self.client = genai.Client(api_key=Config.get_api_key())
        self.model_name = Config.MODEL_NAME

    def analyze_audio(self, file_path: str):
        print(f"Loading '{file_path}' directly into memory...")
        try:
            with open(file_path, "rb") as f:
                audio_data = f.read()
            print("Successfully loaded file into memory!")
        except Exception as e:
            print(f"Failed to read the file: {e}")
            return None

        audio_part = types.Part.from_bytes(
            data=audio_data,
            mime_type='audio/mp3',
        )
        return self._generate_analysis([audio_part, self._get_prompt("audio")])


    def analyze_text(self, text_content: str):
        print("Analyzing text/chat history...")
        return self._generate_analysis([text_content, self._get_prompt("text log or transcript")])


    def _get_prompt(self, media_type="audio"):
        return f"""
        Analyze this {media_type} carefully and evaluate the interaction. 
        1. Identify distinct speakers (e.g., Speaker 1 (Customer), Speaker 2 (Agent)). 
        2. Provide accurate timestamps for each segment (if audio) or line numbers (if text). 
        3. Detect the primary language. 
        4. Identify the primary emotion (Happy, Sad, Angry, Neutral) of the speaker in this segment.
        5. Provide a text transcription for each segment.
        6. DETECT FOUL LANGUAGE: If a speaker uses any foul, offensive, or inappropriate language, strictly highlight it by including a boolean flag `used_foul_language` set to true, and a field `foul_language_detected` containing the exact foul words they used.
        7. Provide a detailed summary of the interaction.
        8. Provide a detailed analysis of the agents' behaviors and a performance rating for each agent.
        9. Analyze how genuine the customer was, their overall behavior, and their final satisfaction level.
        
        Return ALL of this as a structured JSON object. 
        The JSON must have this exact structure:
        {{
            "detailed_summary": {{
                "overall_summary": "Overall detailed summary of the entire conversation.",
                "foul_language_used_anywhere": true,
                "foul_language_details": "Explicitly state who used dirty language and what they said, or None if none was used."
            }},
            "agents_analysis": [
                {{
                    "agent_name": "Name of the agent",
                    "behavior": "Detailed description of the agent's behavior during the call.",
                    "rating": "Overall performance rating out of 10, with justification."
                }}
            ],
            "customer_analysis": {{
                "customer_name": "Name of the customer",
                "genuineness": "Analysis of whether the customer's issues and reactions seem genuine.",
                "behavior": "Detailed description of the customer's behavior and emotional journey.",
                "satisfaction_level": "Assessment of the customer's final satisfaction level (e.g., Dissatisfied, Satisfied, Very Satisfied) and why."
            }},
            "segments": [
                {{
                    "speaker": "Speaker Name",
                    "start_time": "00:00",
                    "end_time": "00:05",
                    "language": "English",
                    "emotion": "Neutral",
                    "text": "Transcription goes here.",
                    "used_foul_language": false,
                    "foul_language_detected": null
                }}
            ]
        }}
        """

    def _generate_analysis(self, contents):
        print("Requesting analysis from the model (this may take a few moments)...")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            
            try:
                if not response.text:
                    raise ValueError("Model returned an empty response.")
                return json.loads(response.text)
            except json.JSONDecodeError:
                error_msg = f"Failed to parse JSON. Raw API response:\n{response.text[:200]}..."
                print(f"Warning: {error_msg}")
                raise ValueError(error_msg)

        except Exception as e:
            print(f"An error occurred during content generation: {e}")
            raise RuntimeError(f"Gemini API Error: {str(e)}")

    def analyze_batch_summaries(self, batch_data: list):
        print("Analyzing combined batch data...")
        prompt = f"""
        You are an expert quality assurance manager. Review the following summaries from {len(batch_data)} separate audio interactions.
        
        Generate an OVERALL SUMMARY with these strict requirements:
        1. State explicitly the total number of audio files processed.
        2. Provide an overall summary of all the customer interactions in these files.
        3. Provide a unified assessment classifying the performance of ALL agents across all files.
        4. CRITICAL: Explicitly state whether ANY agent used foul language in ANY of the files, and if so, who and what was said.
        
        Return exactly in this JSON format:
        {{
            "total_files_analyzed": {len(batch_data)},
            "overall_batch_summary": "Comprehensive summary of what happened across all files.",
            "overall_agent_performance": "Overview of how agents performed collectively across all files.",
            "foul_language_report": {{
                "any_foul_language_used": true/false,
                "details": "Specific details on foul language usage by agents, or 'None detected'."
            }}
        }}
        """
        
        # Convert the batch data to a JSON string to pass to the model
        batch_context = json.dumps(batch_data, indent=2)
        return self._generate_analysis([batch_context, prompt])
