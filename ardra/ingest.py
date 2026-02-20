import os
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions

# Configuration
CHROMA_PATH = "./transight_intelligence_db"
UPLOADS_DIR = "./uploads"

from chromadb.config import Settings
client = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))
from gemini_ef import gemini_ef
collection = client.get_or_create_collection(name="policy_intelligence", embedding_function=gemini_ef)

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text

def chunk_text(text, chunk_size=600, overlap=100):
    """Splits text into smaller pieces with overlap to preserve context."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks

def ingest_all_pdfs():
    for filename in os.listdir(UPLOADS_DIR):
        if filename.endswith(".pdf"):
            print(f"Processing: {filename}...")
            file_path = os.path.join(UPLOADS_DIR, filename)
            
            # Extract and Chunk
            raw_text = extract_text_from_pdf(file_path)
            chunks = chunk_text(raw_text)
            
            # Prepare metadata (tagging by filename/company)
            company_name = filename.replace(".pdf", "").replace("_", " ")
            
            # 2. Add to Vector DB
            collection.add(
                documents=chunks,
                metadatas=[{"source": filename, "company": company_name}] * len(chunks),
                ids=[f"{filename}_{i}" for i in range(len(chunks))]
            )
            print(f"✅ Ingested {len(chunks)} chunks from {filename}")

if __name__ == "__main__":
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    ingest_all_pdfs()