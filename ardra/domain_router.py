from google import genai
from google.genai import types
import json
import chromadb # New Import
from sqlmodel import Session, select
from database import Company, Policy, engine 

client = genai.Client(api_key="AIzaSyB3hGuwRzbrNJxLkvcuuM9tMe36Aniwdjk")

# Using the stable ID to avoid the 404 errors encountered earlier
MODEL_ID = "gemini-3-flash-preview" 

# Setup ChromaDB connection
from chromadb.config import Settings
chroma_client = chromadb.PersistentClient(path="./transight_intelligence_db", settings=Settings(anonymized_telemetry=False))
from gemini_ef import gemini_ef
collection = chroma_client.get_or_create_collection(name="policy_intelligence", embedding_function=gemini_ef)

def identify_domain_and_company(transcript_list):
    full_text = " ".join([item['text'] for item in transcript_list])
    
    prompt = f"""
    TRANSCRIPT: "{full_text}"
    Extract the business domain and company name.
    ALLOWED DOMAINS: [Banking, Telecom, Retail]
    ALLOWED COMPANIES: [Global Trust Bank, Nexus Digital Bank, SkyLink Mobile, Apex Connect, Quest-Shawn]
    Return ONLY JSON: {{"domain": "string", "company": "string or null"}}
    """

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    
    data = json.loads(response.text)
    return data.get('domain'), data.get('company')

def get_transight_vector_context(transcript_list, company_name):
    """New Function: Retrieves semantic context from the Vector DB"""
    full_text = " ".join([item['text'] for item in transcript_list])
    
    # Query the Vector DB for the top 5 most relevant policy chunks
    results = collection.query(
        query_texts=[full_text],
        n_results=5,
        where={"company_name": company_name}
    )
    
    # Combine retrieved chunks into a single string for the prompt
    if results['documents'] and results['documents'][0]:
        return "\n".join(results['documents'][0])
    return "No specific semantic policies found."

def audit_vibe(transcript_list, domain, company_name):
    # 1. Get Semantic context from Vector DB instead of just SQL strings
    semantic_rules = get_transight_vector_context(transcript_list, company_name)
    
    full_transcript = "\n".join([f"{s['speaker']}: {s['text']}" for s in transcript_list])
    
    prompt = f"""
    Role: You are the Astra Security Auditor. Perform a Dual-Gate Audit.
    
    [TRANSCRIPT]
    {full_transcript}

    [RETRIEVED KNOWLEDGE FROM TRANSIGHT DB]
    {semantic_rules}

    GATE 1 (Compliance): Identify violations against retrieved standard operating procedures.
    GATE 2 (Security): Identify data leaks (IPs, internal codes like NE-77, or secrets).

    Return JSON strictly in the format:
    {{
      "audit_results": {{
        "semantic_context_found": "summary of retrieved rules",
        "policy_violations": [
          {{ "rule_breached": "string", "evidence": "quote", "explanation": "string" }}
        ],
        "data_leaks": [
          {{ "leaked_content": "string", "risk_level": "Critical/High", "matched_secret": "string" }}
        ]
      }},
      "overall_safety_rating": "string"
    }}
    """
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)