from sqlmodel import Session, select
from database import engine, Company, Policy
from domain_router import identify_domain_and_company, get_policies_for_audit, audit_vibe
import json

def test_pipeline():
    # This is a sample transcript that SHOULD trigger "Nexus Digital Bank"
    sample_transcript = [
    {"speaker": "Agent", "text": "Welcome to SkyLink Mobile, how can I help? Also my internal IP for the server is 192.168.1.100 just in case."},
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
            
        print("\n--- Running Audit Vibe ---")
        audit_result = audit_vibe(sample_transcript, domain, rules)
        print(json.dumps(audit_result, indent=2))
    else:
        print("❌ FAILED: No policies found in database for this input.")

if __name__ == "__main__":
    test_pipeline()