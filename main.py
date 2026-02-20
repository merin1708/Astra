import json
#from teammate_module import get_audio_analysis # This will be added in 1 hour

def process_full_pipeline(audio_data):
    # 1. Detect Domain (Your Part)
    domain = identify_domain(audio_data)
    print(f"Domain Detected: {domain}")
    
    # 2. Load Policies
    with open('policies.json') as f:
        policy_data = json.load(f)
    
    # 3. Audit Vibe & Compliance (Your Part)
    report = audit_conversation(audio_data, domain, policy_data)
    return report

# For now, test with the sample JSON you shared above
if __name__ == "__main__":
    with open('sample_input.json') as f:
        test_data = json.load(f)
    print(process_full_pipeline(test_data))