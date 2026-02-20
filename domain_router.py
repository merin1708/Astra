from google import genai
from google.genai import types
import json
from sqlmodel import Session, select
from database import Company, Policy, engine 

client = genai.Client(api_key="AIzaSyBGDe60fY6LVZyAFvePAWGZiawAu-Y6NZ8")


MODEL_ID = "gemini-3-flash-preview" 

def identify_domain_and_company(transcript_list):
    full_text = " ".join([item['text'] for item in transcript_list])
    
    # We define exactly what we expect
    prompt = f"""
    TRANSCRIPT: "{full_text}"
    
    INSTRUCTIONS:
    Extract the business domain and company name from the transcript.
    
    ALLOWED DOMAINS: [Banking, Telecom]
    ALLOWED COMPANIES: [Global Trust Bank, Nexus Digital Bank, SkyLink Mobile, Apex Connect]
    
    If no company matches exactly, use null.
    
    RESPONSE FORMAT (JSON ONLY):
    {{
      "domain": "The detected domain",
      "company": "The detected company name"
    }}
    """

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    data = json.loads(response.text)
    # Return the values, not the keys
    return data.get('domain'), data.get('company')

def get_policies_for_audit(domain, company_name):
    with Session(engine) as session:
        # Step 1: Base query for the domain
        statement = select(Policy).join(Company).where(Company.domain == domain)
        
        # Step 2: Only filter by company if we have a valid name
        if company_name and company_name.lower() != "null":
            statement = statement.where(Company.name == company_name)
            
        results = session.exec(statement).all()
        
        combined_rules = []
        for p in results:
            combined_rules.extend(json.loads(p.rules_json))
            
        # Return specific rules or a better fallback
        return combined_rules if combined_rules else ["Agent must be polite and professional."]

def audit_vibe(transcript_list, domain, rules):
    full_transcript = "\n".join([f"{s['speaker']}: {s['text']}" for s in transcript_list])
    
    # Advanced Auditor Prompt
    prompt = f"""
    You are a Compliance Officer for a {domain} company.
    Audit the following transcript against these specific rules: {rules}
    
    Transcript:
    {full_transcript}
    
    Return a JSON object with: 
    - "is_compliant": boolean
    - "score": 1-10
    - "violations": list of strings
    - "agent_eq": short feedback on empathy
    """
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)