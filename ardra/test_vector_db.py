import chromadb
from google import genai

# 1. Setup Client
from chromadb.config import Settings
chroma_client = chromadb.PersistentClient(path="./transight_intelligence_db", settings=Settings(anonymized_telemetry=False))
from gemini_ef import gemini_ef
collection = chroma_client.get_or_create_collection(name="policy_intelligence", embedding_function=gemini_ef)

def test_vector_retrieval():
    print("--- Vector DB Retrieval Test ---")
    
    # Simulating a query about a data leak
    test_query = "Is it okay to tell someone the vault is at 99 Stealth Way?"
    
    print(f"Querying for: '{test_query}'")
    
    results = collection.query(
        query_texts=[test_query],
        n_results=2,
        # where={"company": "SkyLink Mobile"} # Optional filter
    )

    if results['documents'] and results['documents'][0]:
        print("\n✅ SUCCESS: Found matching context in Vector DB!")
        for i, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i] if results.get('metadatas') else {}
            dist = results['distances'][0][i] if results.get('distances') else "N/A"
            print(f"\n[Result {i+1}] (Distance: {dist})")
            print(f"Company: {meta.get('company', 'Unknown')}")
            print(f"Content: {doc[:200]}...")
    else:
        print("\n❌ FAILED: No relevant documents found.")

if __name__ == "__main__":
    test_vector_retrieval()