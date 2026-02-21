# NexaTalk (Project Astra)

**Brief description**: NexaTalk is an enterprise-grade AI auditing ecosystem designed to detect policy violations, analyze agent performance, and prevent sensitive data leaks in customer service interactions using Gemini 3.0 Flash.

## Table of Contents
- [About](#about)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## About
NexaTalk solves the "Semantic Gap" in corporate compliance auditing. While traditional QA tools rely on rigid keyword matching, NexaTalk understands the semantic intent of conversations. It cross-references live call transcripts and chat logs against a library of specific company rules and Standard Operating Procedures (SOPs) stored in a RAG-enabled database. 

It ensures that agents follow mandatory procedures (like verifying IDs) and never disclose sensitive internal data (like dropship warehouse statuses, private IPs, or security codes).

## Key Features
- **Semantic Dual-Gate Auditing**: Simultaneously verifies *SOP Compliance* (did they follow rules?) and *Data Security* (did they leak secrets?).
- **Dynamic Context Routing**: Automatically detects the Business Domain (e.g., Retail, Banking) and Company Name directly from the dialogue to load the correct rulebook.
- **Rules-as-Code Database**: Employs an intelligent SQL/Vector RAG database to map dynamic, company-specific policies into active prompt configurations.
- **Emotion & Sentiment Analysis**: Detects customer emotions segment-by-segment to track de-escalation efficiency and flag unprofessional agent conduct or foul language.
- **Automated RCA**: Generates actionable RCA (Root Cause Analysis) insights and JSON reports containing precise evidence quotes and severity scores.

## Architecture
The NexaTalk system operates on a multi-stage, AI-driven pipeline:

1. **Ingestion & Pre-processing (`ProcessingInput`)**:
   - A Flask application (`app.py`) accepts audio files or text transcripts.
   - It performs initial speech-to-text, speaker diarization, and emotion classification, outputting a structured, timestamped array of dialogue (`main_output.json`).

2. **The Intelligence Controller (`ardra/automated_pipeline.py`)**:
   - Acts as the central nervous system, automatically triggering the audit phase once data is processed.

3. **Dynamic Domain Routing (`ardra/domain_router.py`)**:
   - Uses Gemini to semantically analyze the isolated transcript to identify the active Company and Sector.

4. **Configurable Client Context (Policy Retrieval)**:
   - Queries the local `transight_intelligence.db` via SQLModel. The system uses a **simple, highly configurable database schema** to store and map localized Standard Operating Procedures and Security rules. This allows new clients or rulebooks to be onboarded instantly without retraining the AI models.
   
   **Database Schema (`database.py`):**
   - **`Company` Table**: Stores the core client information.
     - `id` (Primary Key, Integer)
     - `name` (String, Indexed) - e.g., "Quest-Shawn"
     - `domain` (String) - e.g., "Retail", "Banking"
   - **`Product` Table**: Stores products associated with a specific company.
     - `id` (Primary Key, Integer)
     - `company_id` (Foreign Key, Integer)
     - `product_name` (String)
     - `description` (String)
   - **`Policy` Table**: Stores business rules and mandatory compliance steps.
     - `id` (Primary Key, Integer)
     - `company_id` (Foreign Key, Integer)
     - `policy_type` (String) - e.g., "Identity Verification", "Security & Secrets", "Return & Refund"
     - `rules_json` (String) - The exact mandatory compliance steps stored as a flexible JSON string for direct injection into the LLM prompt.

5. **The Semantic Dual-Gate Audit**:
   - Injects both the isolated transcript and specific retrieved policies into a sophisticated auditing LLM prompt.
   - Outputs highly detailed findings indicating missed procedures or leaked company secrets.

## Tech Stack
- **Core Orchestration**: Python 3.11, FastAPI, Flask
- **LLM Engine**: Google Gemini 3.0 Flash Preview (Google GenAI SDK)
- **Database (Policies & RAG)**: SQLite + SQLModel
- **Audio Processing**: WhisperX, pyannote-audio, Hugging Face
- **Frontend Visualization**: Custom HTML5, Vanilla JavaScript, Chart.js, Tailwind/Custom CSS

## Installation & Setup

### Prerequisites
- Python 3.11+
- Google Gemini API Key
- Supported libraries (see `requirements.txt`)

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/merin1708/Astra.git
   ```
2. **Setup the Core Services:**
   Navigate to the intelligence engine directory:
   ```bash
   cd Astra/ardra
   pip install google-genai sqlmodel pypdf chromadb fastapi uvicorn
   ```
3. **Seed the Database:**
   Populate the SQLite policy database with the mock company rules:
   ```bash
   python seed.py
   ```
4. **Setup the Input Processor:**
   ```bash
   cd ../ProcessingInput
   pip install flask werkzeug
   ```

## Usage

You can run the full ecosystem from the root processing application:

```bash
cd Astra/ProcessingInput
python app.py
```
- Open `http://127.0.0.1:8000` in your web browser.
- Upload an audio file or paste a text transcript.
- The pipeline will automatically transcribe, detect the company, evaluate compliance against SQL rules, and output a detailed dashboard analysis alongside `.json` reports in the `output/` directory.

Alternatively, to run just the audit controller on existing transcripts:
```bash
cd Astra/ardra
python automated_pipeline.py
```

## Contributing
Contributions are welcome. Please open an issue or submit a pull request for improvements to the prompt pipeline, UI features, or RAG models.

## License
[MIT License](LICENSE)

## Contact
Team Astra Project Link: [https://github.com/merin1708/Astra](https://github.com/merin1708/Astra)
