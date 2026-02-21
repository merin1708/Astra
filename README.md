# 🎙️ OmniContext API: Agentic AI Conversation Intelligence

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg) ![Gemini](https://img.shields.io/badge/AI-Google_Gemini_1.5-orange.svg) ![Status](https://img.shields.io/badge/Status-Enterprise_Ready-success.svg)

> **Transight Hackathon Submission** > A decoupled, zero-downtime backend API that bypasses legacy speech-to-text pipelines by feeding raw audio directly into a Multimodal LLM to extract highly structured, business-critical insights and drive real-time AI Fraud & Scam Detection.

## 🚀 The Vision

Traditional customer support pipelines rely on fragile NLP steps (Speech-to-Text → Translation → Sentiment). This loses the acoustic reality of the call—the tone, the pauses, and the panic. 

**OmniContext API** is an Agentic, RAG-augmented Multimodal Pipeline. It ingests raw audio and a dynamic "Client Context" JSON, allowing the AI to instantly adapt its analysis to the enterprise's specific business rules (e.g., Telecom Billing vs. Banking Fraud Detection) in a single, lightning-fast pass. 

---

## ✨ Enterprise-Grade Features

* **Native Multimodal Processing:** No Whisper. No Pyannote. The system natively comprehends audio files and code-switched languages (e.g., Manglish) in a single API call.
* **AI Fraud & Scam Detection:** Actively shields vulnerable demographics. By passing dynamic fraud rules into the multimodal pipeline, the system instantly catches real-time scam attempts, social engineering tactics, or unauthorized OTP requests.
* **Zero-Downtime Configuration:** API keys and business rules are injected on a strictly *per-request* basis. Enterprises can rotate compromised keys or update compliance rules without rebooting the live server.
* **Dynamic Rule Retrieval (Schema Injection):** The client dictates the output. Pass `["competitor_mentions", "foul_language"]` in the request payload, and the AI dynamically tracks those exact metrics.
* **Rate-Limit Immunity:** Built-in network fault tolerance. If the LLM API throttles the connection, the backend intercepts the crash and dynamically generates a fallback JSON report rather than dropping the HTTP request.
* **Self-Healing Output Auditor:** LLMs hallucinate; our API does not. An internal middleware sanitizes the LLM output, strips rogue markdown blocks, and guarantees 100% strict JSON compliance.

---

## 🏗️ Technical Architecture

This backend is built for speed, resilience, and horizontal scaling.

1. **Routing Layer (FastAPI):** Handles robust data validation (Pydantic), asynchronous request management, and automated OpenAPI documentation.
2. **AI Service Engine (Google GenAI SDK):** Wraps the multimodal prompt, combining the raw audio stream with the injected client business policies.
3. **Data Persistence (Flat-File NoSQL):** To maximize speed and avoid DB connection overhead during the hackathon, state is managed via an atomic, file-by-file JSON caching system. 

### 🧠 AI Usage Approach & Configuration Mechanism
We treat the client's JSON configuration as dynamic context. When the API receives a request, it parses the client's specific `risk_triggers` and `policies` and injects them into the master prompt as system instructions. The Multimodal API evaluates the conversation exclusively through the lens of those injected rules.

---

## ⚙️ Quick Start

### 1. Clone & Install
```bash
git clone [https://github.com/yourusername/omnicontext-api.git](https://github.com/yourusername/omnicontext-api.git)
cd omnicontext-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn python-multipart pydantic google-generativeai python-dotenv
