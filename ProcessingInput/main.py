import os
import json
from src.services.gemini_service import GeminiService

def main():
    audio_file_path = "audio_file.mp3"
    
    if not os.path.exists(audio_file_path):
        print(f"File not found: {audio_file_path}")
        print("Please make sure the file is in the same directory as this script.")
        return

    try:
        service = GeminiService()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    result = service.analyze_audio(audio_file_path)
    
    if result:
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save raw JSON
        output_file = os.path.join(output_dir, 'audio_analysis.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
        print(f"\nSuccessfully saved the full JSON result to '{output_file}'")

        # Extract only the detailed metrics
        detailed_summary_data = {
            "detailed_summary": result.get("detailed_summary", {}),
            "agents_analysis": result.get("agents_analysis", []),
            "customer_analysis": result.get("customer_analysis", {})
        }

        # Generate Detailed Summary JSON
        summary_file = os.path.join(output_dir, 'detailed_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
             json.dump(detailed_summary_data, f, indent=4)
            
        print(f"Successfully saved the detailed summary report to '{summary_file}'")

if __name__ == "__main__":
    main()
