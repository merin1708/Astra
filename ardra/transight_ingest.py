import chromadb
from sqlmodel import Session
from database import engine, Company, Policy # Your existing SQLite models

# Connect to the Transight Vector Engine
transight_vector_client = chromadb.PersistentClient(path="./transight_intelligence_db")
collection = transight_vector_client.get_or_create_collection(name="policy_intelligence")

def ingest_to_transight(company_name, domain, pdf_text):
    # 1. Store the high-level metadata in SQL (Structured)
    with Session(engine) as session:
        company = Company(name=company_name, domain=domain)
        session.add(company)
        session.commit()
        session.refresh(company)

    # 2. Store the semantic policy in the Vector DB (Unstructured)
    # We split text into chunks to help the AI find specific breaches later
    chunks = [pdf_text[i:i+500] for i in range(0, len(pdf_text), 400)]
    
    collection.add(
        documents=chunks,
        metadatas=[{"company_id": company.id, "company_name": company_name}] * len(chunks),
        ids=[f"{company_name}_{i}" for i in range(len(chunks))]
    )
    print(f"✅ Data successfully ingested into Transight Intelligence DB for {company_name}")