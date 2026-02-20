from sqlmodel import Session, select
from database import engine, Company, Policy
from domain_router import identify_domain_and_company, get_policies_for_audit
import json

def test_pipeline():
    # This is a sample transcript that SHOULD trigger "Nexus Digital Bank"
    sample_transcript = [
    {"speaker": "Agent", "text": "Welcome to SkyLink Mobile, how can I help?"},
    {"speaker": "Customer", "text": "My 5G plan isn't working."}]

    print("--- Starting Integration Test ---")

    # Step 1: Check if AI detects the Company and Domain
    domain, company = identify_domain_and_company(sample_transcript)
    print(f"Detected: {domain} | Company: {company}")

    # Step 2: Fetch the policies from the SQLite DB your friend seeded
    rules = get_policies_for_audit(domain, company)
    
    if rules:
        print(f"Successfully retrieved {len(rules)} rules for {company or domain}")
        print(f"Sample Rule: {rules[0]}")
        
        # Verify specific fintech rule from your friend's seed data
        if any("seed phrase" in r.lower() for r in rules):
            print("✅ SUCCESS: Correct policies retrieved from SQLite!")
    else:
        print("❌ FAILED: No policies found in database for this input.")

if __name__ == "__main__":
    test_pipeline()