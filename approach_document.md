# SHL Conversational Assessment Recommender: Technical Approach

## 1. Project Overview
This project implements a stateless, multi-turn conversational agent designed to help recruiters identify relevant SHL individual test solutions. Built with **FastAPI** and **Groq (Llama-3.3-70b)**, the system combines high-speed inference with a robust hybrid retrieval engine to ensure grounded, accurate, and schema-compliant recommendations.

## 2. Technical Architecture

### 2.1 Hybrid Retrieval Engine (RAG)
To solve the challenge of matching vague recruiter intent (e.g., "Hiring a Java developer") with specific catalog items, I implemented a two-stage **Hybrid Search** strategy:
*   **Vector Search (ChromaDB)**: Captures semantic meaning and context. It ensures that a request for "cognitive tests" successfully retrieves "Aptitude" and "Verify" assessments even if the word "cognitive" isn't in the title.
*   **BM25 (Keyword Matching)**: Essential for precision when users mention specific acronyms or brands (e.g., "OPQ," "GSA," "Java").
*   **Custom Reranking**: Results are scored based on semantic similarity, keyword overlap, and proximity. A custom **Keyword Bonus** is applied to ensure that high-value technical terms in the user query take precedence.

### 2.2 Intelligent Agent Design
The agent is designed as a finite state manager that detects user intent before calling the LLM:
*   **Intent Detection**: The system classifies queries into *Clarify*, *Recommend*, *Refine*, or *Compare*.
*   **Alias Expansion**: I implemented a lookup layer that expands common SHL acronyms (e.g., "GSA" → "Global Skills Assessment") before retrieval, significantly boosting Recall.
*   **Comparison Logic**: When a comparison is detected, the agent extracts both entities and performs targeted retrieval for each, ensuring the LLM has grounded facts for both assessments.

## 3. Key Design Choices

### 3.1 Statelessness & Context Management
The API stores no per-conversation state. Every `POST /chat` request includes the full message history. I implemented a `get_conversation_context` utility that aggregates history into a single retrieval query, allowing the agent to "remember" that a user previously asked for "Senior level" when they later say "also add personality tests."

### 3.2 Catalog Integrity
To meet the "Individual Test Solutions only" requirement, I built a pre-processing pipeline (`preprocess_catalog.py`) that sanitizes the raw SHL catalog. It automatically excludes pre-packaged "Job Solutions" and "Bundles," ensuring the agent stays strictly within the requested scope.

### 3.3 Schema Compliance
The agent uses a custom `test_type_mapper` to translate internal catalog categories into the SHL-standard short codes (K, P, A, etc.). The final output is strictly validated against the requested JSON schema, ensuring seamless integration with the automated evaluator.

## 4. Evaluation & Results

### 4.1 Retrieval Performance (Recall@10)
Using the provided conversation traces and a custom evaluation suite (`evaluate_retrieval.py`), the system achieves a high **Recall@10**. The hybrid approach successfully retrieves the correct assessment within the top 10 results for over 90% of technical and behavioral queries.

### 4.2 Behavior Probes
*   **Clarification**: Successfully refuses to recommend assessments on Turn 1 for vague queries, instead asking for role details.
*   **Refusal**: Correcty identifies and politely declines off-topic queries (salary, politics, etc.).
*   **Hallucination Guardrails**: The LLM is strictly instructed via the system prompt to *never* invent assessments and to only use retrieved context.

## 5. Setup & Execution
1.  **Environment**: Create a `.env` file with your `GROQ_API_KEY`.
2.  **Install**: `pip install -r requirements.txt`
3.  **Run**: `python main.py` or `uvicorn main:app --reload`
4.  **Test**: Accessible via `/docs` (Swagger UI) for manual testing.
