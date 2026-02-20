import os
import json
from datetime import datetime
from google import genai
from google.genai import types

from sqlmodel import Session, select
from database import engine, Company, Policy

from domain_router import identify_domain_and_company

MODEL_ID = "gemini-3-flash-preview"
client = genai.Client(api_key="AIzaSyB3hGuwRzbrNJxLkvcuuM9tMe36Aniwdjk")

AUDIO_JSON_PATH = "../ProcessingInput/output/audio_analysis.json"
OUTPUT_DIR = "./output"
OUTPUT_JSON_PATH = os.path.join(OUTPUT_DIR, "audit_results.json")

def automated_pipeline():
    print("🚀 Astra Intelligence Pipeline Controller Initializing...")

    # Phase 1: Input Orchestration
    print(f"📄 Phase 1: Reading input from {AUDIO_JSON_PATH}")
    if not os.path.exists(AUDIO_JSON_PATH):
        print(f"❌ ERROR: {AUDIO_JSON_PATH} not found!")
        return

    with open(AUDIO_JSON_PATH, "r", encoding="utf-8") as f:
        audio_data = json.load(f)

    transcript_list = audio_data.get("segments", [])
    full_transcript = "\n".join([f"[{s['emotion']}] {s['speaker']}: {s['text']}" for s in transcript_list])
    
    # Phase 2: Contextual SQL Retrieval
    print("🔍 Phase 2: Contextual SQL Retrieval")
    domain, company_name = identify_domain_and_company(transcript_list)
    print(f"Domain mapped: {domain} | Company: {company_name}")

    if not company_name:
        print("❌ ERROR: Could not identify company from transcript.")
        return

    rules_text = ""
    with Session(engine) as session:
        statement = select(Company).where(Company.name == company_name)
        company = session.exec(statement).first()
        
        if company:
            policies = session.exec(select(Policy).where(Policy.company_id == company.id)).all()
            mandatory_constraints = []
            for p in policies:
                try:
                    rules = json.loads(p.rules_json)
                    formatted_rules = json.dumps(rules, indent=2)
                except:
                    formatted_rules = p.rules_json
                mandatory_constraints.append(f"--- Policy Type: {p.policy_type} ---\n{formatted_rules}")
            
            rules_text = "\n\n".join(mandatory_constraints)
        else:
            print(f"⚠️ Warning: Company '{company_name}' not found in SQL database.")

    print(f"📚 Retrieved Context length from SQL DB: {len(rules_text)} chars")

    # Phase 3: The Audit Analysis
    print("⚖️ Phase 3: SQL Rules Security & Compliance Audit execution...")
    
    prompt = f"""
    Role: You are the Astra Intelligence Pipeline Controller.
    Your objective is to automate the compliance audit of customer service calls using structured business rules.

    [TRANSCRIPT (with explicit emotional weight)]
    {full_transcript}

    [MANDATORY CONSTRAINTS (from SQL Database)]
    {rules_text}

    Evaluate the conversation against the retrieved SQL rules using two primary lenses:
    Constraint Check: Did the agent perform the specific actions required (e.g., verifying an Order ID starting with 'QS-')?
    Security & Leak Detection: Using the 'Security & Secrets' policy type (if provided), identify if the agent revealed internal data like warehouse locations, IP addresses, or private bypass codes.

    Phase 4: Standardized JSON Output
    Output strictly valid JSON matching this schema exactly. No markdown blocks, no other text.
    {{
      "audit_metadata": {{
        "detected_company": "{company_name}",
        "detected_domain": "{domain}",
        "total_violations": 0
      }},
      "compliance_findings": [
        {{
          "policy_type": "string",
          "violation": true/false,
          "evidence": "exact quote from transcript",
          "severity": "Low/Medium/High",
          "remediation": "how the agent should have handled this"
        }}
      ],
      "security_leaks": [
        {{
          "secret_disclosed": "string",
          "risk_score": "0-100",
          "impact_summary": "string"
        }}
      ]
    }}
    """

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    
    # Phase 4: Standardized Output Generation
    print("📁 Phase 4: Standardized Output Generation")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    audit_json = json.loads(response.text)
    
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_json, f, indent=2)
        
    print(f"✅ SUCCESS: Full audit lifecycle complete. Results written to {OUTPUT_JSON_PATH}")
    print("\n--- Pipeline Audit Summary ---")
    print(json.dumps(audit_json, indent=2))

if __name__ == "__main__":
    automated_pipeline()
