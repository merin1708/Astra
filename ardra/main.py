import json
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from google import genai
from google.genai import types

# Import your teammate's database setup
from database import Company, Policy, engine 

# Initialize Gemini Client (New SDK for Gemini 2.0/3.0 Flash)
client = genai.Client(api_key="AIzaSyBGDe60fY6LVZyAFvePAWGZiawAu-Y6NZ8")
MODEL_ID = "gemini-3-flash-preview"  # Using the latest Flash Preview endpoint

app = FastAPI(title="Astra Conversation Intelligence API")

def identify_context(transcript_text: str):
    """Uses Gemini to identify the Domain and Company from the transcript."""
    prompt = f"""
    Analyze the following transcript and identify:
    1. The business domain (Banking, Telecom, or Retail).
    2. The specific company name if mentioned.
    
    Transcript: {transcript_text}
    
    Return ONLY a JSON object: {{"domain": "string", "company": "string or null"}}
    """
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

def get_db_policies(domain: str, company_name: str = None):
    """Queries SQLModel to find the specific business rules."""
    with Session(engine) as session:
        # Step 1: Find company ID
        company_stmt = select(Company).where(Company.domain == domain)
        if company_name:
            company_stmt = company_stmt.where(Company.name == company_name)
        
        company = session.exec(company_stmt).first()
        
        if not company:
            return []

        # Step 2: Fetch policies for that company
        policy_stmt = select(Policy).where(Policy.company_id == company.id)
        policies = session.exec(policy_stmt).all()
        
        # Flatten the rules_json into a single list
        all_rules = []
        for p in policies:
            all_rules.extend(json.loads(p.rules_json))
        return all_rules

@app.post("/analyze")
async def analyze_conversation(transcript_data: list):
    """
    Main Endpoint: Receives teammate's audio analysis output and audits it.
    Input Format: [{"speaker": "...", "text": "...", "emotion": "..."}]
    """
    try:
        # 1. Prepare raw text for the AI
        full_transcript = "\n".join([f"{s['speaker']}: {s['text']}" for s in transcript_data])
        
        # 2. Identify who we are talking to (Agentic Routing)
        context = identify_context(full_transcript)
        
        # 3. Retrieve policies from SQLite (RAG-lite)
        rules = get_db_policies(context['domain'], context['company'])
        
        # 4. Perform the Final Audit
        audit_prompt = f"""
        Domain: {context['domain']}
        Company: {context['company']}
        Policies: {rules}
        
        Audit this transcript for compliance and emotional intelligence:
        {full_transcript}
        
        Return a JSON report including: 
        - 'is_compliant' (bool)
        - 'violations' (list)
        - 'sentiment_trend' (how the vibe changed)
        - 'summary' (max 2 sentences)
        """
        
        audit_response = client.models.generate_content(
            model=MODEL_ID,
            contents=audit_prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        report = json.loads(audit_response.text)
        
        return {
            "status": "success",
            "metadata": context,
            "rules_checked": len(rules),
            "analysis": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)