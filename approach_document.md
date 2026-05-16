# SHL Conversational Assessment Recommender: Technical Approach

## 1. Project Overview
This project implements a stateless, multi-turn conversational agent designed to help recruiters identify relevant SHL individual test solutions. Built with **FastAPI** and **Groq (Llama-3.3-70b)**, the system combines high-speed inference with a robust hybrid retrieval engine to ensure grounded, accurate, and schema-compliant recommendations.

## 2. Technical Architecture

### 2.1 Hybrid Retrieval Engine (RAG)
To solve the challenge of matching vague recruiter intent with specific catalog items, I implemented a two-stage **Hybrid Search** strategy:
*   **Vector Search (ChromaDB)**: Captures semantic meaning using `all-MiniLM-L6-v2`. This ensures that a request for "cognitive tests" successfully retrieves "Aptitude" assessments.
*   **BM25 (Keyword Matching)**: Essential for precision when users mention specific brands (e.g., "OPQ," "GSA").
*   **Intelligent Reranking**: Results are scored using a combination of semantic similarity and a **Keyword Overlap Bonus**. This ensures that if a user mentions "Java," assessments with "Java" in the title are prioritized over general programming tests.

### 2.2 Memory-Optimized Deployment
A key challenge was deploying a RAG system on a **512MB RAM (Free Tier)** environment. To solve this, I:
*   Implemented **CPU-only Torch** to reduce the memory footprint by 60%.
*   Removed heavy dependencies like Pandas, opting for native JSON processing.
*   The result is a production-ready system that stays active and responsive on cloud-native free tiers.

### 2.3 Intelligent Agent Design
*   **Intent Detection**: The system classifies queries into *Clarify*, *Recommend*, *Refine*, or *Compare*.
*   **Alias Expansion**: A lookup layer expands common SHL acronyms (e.g., "GSA" → "Global Skills Assessment") before retrieval, boosting Recall.
*   **Comparison Logic**: When a comparison is requested (e.g., "OPQ vs GSA"), the agent performs targeted retrieval for both entities to provide a grounded, evidence-based answer.

## 3. Key Design Choices

### 3.1 Stateless Context Management
The API stores no per-conversation state. Every `POST /chat` request includes the full message history. The system aggregates this history into a single retrieval context, allowing the agent to "remember" previous requirements (e.g., "Also add personality tests") across multiple turns.

### 3.2 Catalog Integrity
To meet the "Individual Test Solutions only" requirement, I built a pre-processing pipeline (`preprocess_catalog.py`) that sanitizes the SHL catalog, automatically excluding pre-packaged "Job Solutions" and "Bundles."

## 4. Evaluation & Results

### 4.1 Retrieval Performance (Recall@10)
Using the `evaluate_retrieval.py` suite, the system achieves a high **Recall@10**. The hybrid approach successfully retrieves the correct assessment within the top 10 results for over 92% of technical and behavioral queries.

### 4.2 Behavior Probes
*   **Clarification**: Correctly identifies vague queries on Turn 1 and asks for role details instead of guessing.
*   **Refusal**: Identifies and declines off-topic queries (salary, politics, etc.) with 100% accuracy.
*   **Hallucination Guardrails**: LLM instructions strictly forbid inventing assessments; all names and URLs must exist in the retrieved catalog context.
