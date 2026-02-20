import os
import json
import glob
from src.services.gemini_service import GeminiService

def main():
    # Resolve paths relative to the script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(base_dir, "audiofiles")
    output_dir = os.path.join(base_dir, "output")
    
    if not os.path.exists(audio_dir):
        print(f"Directory not found: {audio_dir}")
        print("Please create an 'audiofiles' directory and add your files.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get all potential audio files (mp3, wav, mpeg)
    audio_files = []
    for ext in ('*.mp3', '*.wav', '*.mpeg', '*.m4a'):
        audio_files.extend(glob.glob(os.path.join(audio_dir, ext)))

    if not audio_files:
        print(f"No audio files found in '{audio_dir}'.")
        return

    try:
        service = GeminiService()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    print(f"Found {len(audio_files)} audio files. Starting processing...")
    
    all_summaries = []

    for file_path in audio_files:
        filename = os.path.basename(file_path)
        print(f"\n--- Processing: {filename} ---")
        
        # Analyze individual file
        result = service.analyze_audio(file_path)
        
        if result:
            # We want to extract the detailed metrics to save as individual file output
            # and to pass to the final batch analyzer
            detailed_summary_data = {
                "file_name": filename,
                "detailed_summary": result.get("detailed_summary", {}),
                "agents_analysis": result.get("agents_analysis", []),
                "customer_analysis": result.get("customer_analysis", {}),
                "segments": result.get("segments", [])
            }
            
            all_summaries.append(detailed_summary_data)
            
            # Save individual summary
            sanitized_name = os.path.splitext(filename)[0].replace(" ", "_")
            summary_file = os.path.join(output_dir, f'summary_{sanitized_name}.json')
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_summary_data, f, indent=4)
                
            print(f"Saved individual summary to '{summary_file}'")
        else:
             print(f"Failed to process {filename}")

    # Generate overarching summary
    if all_summaries:
        print("\n--- Generating Overall Batch Summary ---")
        overall_result = service.analyze_batch_summaries(all_summaries)
        
        if overall_result:
            overall_file = os.path.join(output_dir, 'overall_summary.json')
            with open(overall_file, 'w', encoding='utf-8') as f:
                json.dump(overall_result, f, indent=4)
            print(f"\nSuccessfully saved the OVERALL batch summary to '{overall_file}'")
            
            # Print highlights to console
            print("\n" + "="*50)
            print("BATCH PROCESSING COMPLETE")
            print("="*50)
            print(f"Total files analyzed: {overall_result.get('total_files_analyzed', len(all_summaries))}")
            print(f"\nOverall Agent Performance:\n{overall_result.get('overall_agent_performance', 'N/A')}")
            foul_report = overall_result.get('foul_language_report', {})
            used_foul = foul_report.get('any_foul_language_used', False)
            print(f"\nFoul Language Detected: {'YES WARNING' if used_foul else 'No'}")
            print(f"Details: {foul_report.get('details', 'N/A')}")
            print("="*50)

if __name__ == "__main__":
    main()
