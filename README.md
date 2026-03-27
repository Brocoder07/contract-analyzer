📜 Contract Analyzer: SLM-Powered Legal Intelligence
Contract Analyzer is a high-performance, action-oriented platform built to automate legal document auditing, risk detection, and clause optimization. Developed by Team Secondbenchers, the system utilizes optimized Small Language Models (SLMs) and Hybrid Analysis to provide professional-grade legal insights with low latency.

🚀 Key Features
Hybrid Risk Detection: Uses a dual-layered approach combining a deterministic Rule Engine for explicit violations and a Machine Learning Model for nuanced semantic risks.

Actionable Smart Editor: Beyond identification, the system suggests programmatically valid replacements for risky clauses. Users can apply these fixes directly within the UI and export a corrected .docx file.

SLM Optimization: Optimized for speed and privacy by utilizing Small Language Models (T5, BART, Pegasus) instead of traditional, heavy BERT models.

Multi-Format Processing: Seamlessly extracts and processes text from PDF, DOCX, and TXT formats.

🏗️ System Architecture
The project is built on a decoupled, modular architecture to ensure scalability and maintainability.

1. Frontend (Presentation Layer)
Framework: React.js with TypeScript.

State Management: Centralized management of document state and analysis results.

UI/UX: Custom components for PDF visualization and a "Diff-style" Suggestion Interface.

2. Backend (Application Layer)
Server: FastAPI (Python) providing asynchronous high-speed API endpoints.

Services: Modular services for Document Processing, AI Analysis, and the OOP-based Document Editing Engine.

3. AI Layer (Intelligence Layer)
Hybrid Analyzer: Coordinates the Rule Engine and SLM wrappers.

Models:

T5: Logic for generating legal-compliant clause suggestions.

BART/Pegasus: Used for contextual summarization of dense legal blocks.

SpaCy: Handles initial NLP tokenization and linguistic analysis.

🔄 System Workflow
Ingestion: User uploads a legal document. The DocumentProcessor identifies the format and extracts clean text.

Hybrid Analysis:

The Rule Engine scans for specific keywords and regex patterns.

The SLM Model performs semantic classification to detect hidden risks like Indemnification or Unfair Termination.

Suggestion Generation: For every detected risk, the T5-based Suggestion Model generates a "Safe" version of the clause.

Review & Selection: The user reviews the risks and chooses which AI suggestions to accept.

Programmatic Editing: The DocumentEditor service applies selected changes using a Reverse-Index Sorting algorithm to maintain document integrity.

Export: The finalized text is repacked into a .docx file and returned to the user.

🛠️ Tech Stack
Backend: FastAPI, PyTorch, Transformers, SpaCy, SQLAlchemy.

Frontend: React (Vite), TypeScript, Lucide React, CSS Modules.

DevOps/Tools: Git, GitHub, Python Venv.

📥 Getting Started
Backend Setup -

cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend Setup -

cd frontend
npm install
npm run dev
