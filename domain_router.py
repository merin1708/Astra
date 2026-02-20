import google.generativeai as genai

# Use the Gemini API (Free Tier)
genai.configure(api_key="AIzaSyAfPXR7LiMTACkM0rKQgfrzvh3ena5LSRk")

def identify_domain(transcript_list):
    # 1. Join all text parts into one transcript
    full_text = " ".join([item['text'] for item in transcript_list])
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 2. Agentic Prompt for Classification
    prompt = f"""
    Categorize this customer support transcript into one of these domains: 
    [Banking, Telecom, Insurance, Retail, Other].
    
    Transcript: {full_text}
    
    Return only the domain name.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()
import sqlite3

def get_policies_from_db(domain):
    """
    Connects to the SQLite database and fetches rules for the detected domain.
    """
    try:
        # Connect to the database file your teammate is creating
        conn = sqlite3.connect('transight_intelligence.db') 
        cursor = conn.cursor()
        
        # Query to find rules based on the domain
        query = "SELECT rules FROM policies WHERE domain = ?"
        cursor.execute(query, (domain,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Assuming rules are stored as a string or comma-separated list
            return result[0] 
        return "Follow general customer service excellence."
        
    except Exception as e:
        print(f"Database error: {e}")
        return "Follow general customer service excellence."
def audit_conversation(transcript_list, domain): # Removed policy_data parameter
    # 1. NEW: Get rules from SQLite instead of JSON
    rules = get_policies_from_db(domain)
    
    full_transcript = "\n".join([f"{s['speaker']}: {s['text']}" for s in transcript_list])
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 2. The rest of your prompt remains the same
    audit_prompt = f"""
    You are a QA Auditor for {domain} support.
    RULES: {rules}
    TRANSCRIPT: {full_transcript}
    ...
    """
    # (Rest of the function logic stays the same)
    return response.text