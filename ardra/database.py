from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
import json

# --- 1. Database Models (Schema) ---

class Company(SQLModel, table=True):
    """Stores the core client information."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    domain: str # e.g., "Banking", "Telecom"

class Product(SQLModel, table=True):
    """Stores products associated with a specific company."""
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id")
    product_name: str
    description: str

class Policy(SQLModel, table=True):
    """Stores business rules and mandatory compliance steps."""
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id")
    policy_type: str # e.g., "Identity Verification", "Refunds"
    # We store rules as a JSON string to keep them flexible for the LLM
    rules_json: str 

# --- 2. Database Setup ---

sqlite_file_name = "transight_intelligence.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- 3. Retrieval Logic (The "R" in RAG) ---

def get_client_context(company_name: str):
    """
    Retrieves all relevant facts for a company to feed into the AI prompt.
    This fulfills the 'Configurable Client Context' requirement.
    """
    with Session(engine) as session:
        # Find Company
        statement = select(Company).where(Company.name == company_name)
        company = session.exec(statement).first()
        
        if not company:
            return None

        # Retrieve associated Products and Policies
        products = session.exec(select(Product).where(Product.company_id == company.id)).all()
        policies = session.exec(select(Policy).where(Policy.company_id == company.id)).all()

        return {
            "domain": company.domain,
            "products": [p.product_name for p in products],
            "policies": [json.loads(pol.rules_json) for pol in policies]
        }