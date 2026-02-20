import json
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from google import genai
from google.genai import types

# Import your teammate's database setup
from database import Company, Policy, engine 

# Initialize Gemini Client (New SDK for Gemini 2.0/3.0 Flash)
client = genai.Client(api_key="AIzaSyB3hGuwRzbrNJxLkvcuuM9tMe36Aniwdjk")
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
        Role: You are the Astra Vector-RAG Integration Specialist. Your task is to implement a semantic auditing system that detects policy violations and internal data leaks by comparing conversation transcripts against a vector-indexed knowledge base of company PDFs.

        Phase 1: Vector Knowledge Ingestion
        Document Chunking: Process uploaded PDF policy manuals by breaking them into overlapping chunks (approx. 500 tokens each) to preserve context.
        Embedding Generation: Use a high-density embedding model to convert these chunks into vectors.
        Metadata Tagging: Store each vector with metadata tags including company_name, policy_type (e.g., Compliance, Privacy, Security), and source_page.

        Phase 2: Semantic Retrieval Logic
        Query Synthesis: When a transcript is received, generate a "Search Query" that summarizes the core actions of the agent.
        Similarity Search: Perform a Vector Search to retrieve the top 5 most relevant policy chunks based on the meaning of the conversation, not just keywords.
        Leakage Detection: Specifically query the "Security" collection for any overlaps between the transcript and sensitive company data (e.g., internal IPs, private project names).

        Phase 3: The "Dual-Gate" Audit
        Analyze the transcript against the retrieved context to produce a JSON report:
        Gate 1 (Compliance): Did the agent deviate from the retrieved "Standard Operating Procedures"?
        Gate 2 (Security): Did the agent mention any information that semantically matches a "Company Secret" chunk?

        Phase 4: Structured Output (JSON)
        Output the results in this strict format:

        JSON
        {{
          "audit_results": {{
            "semantic_context_found": "list of retrieved policy titles",
            "policy_violations": [
              {{
                "rule_breached": "string",
                "semantic_match_score": "0.0-1.0",
                "evidence": "transcript quote",
                "explanation": "why this is a breach based on the PDF"
              }}
            ],
            "data_leaks": [
              {{
                "leaked_content": "string",
                "risk_level": "Critical/High",
                "matched_secret_from_pdf": "string"
              }}
            ]
          }},
          "overall_safety_rating": "string"
        }}

        TRANSCRIPT:
        {full_transcript}

        RETRIEVED POLICIES (Simulated Vector Search Results):
        {rules}
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