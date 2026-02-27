📜 Contract Analyzer
Contract Analyzer is an advanced, AI-powered platform designed to automate the semantic annotation, risk assessment, and modification of legal documents. Developed as a final-year major project by Team Secondbenchers, the system transitions from standard BERT-based models to an optimized Small Language Model (SLM) architecture to provide high-speed, high-accuracy legal insights.

🚀 Key Features
Hybrid Risk Analysis Engine: Combines a deterministic Rule Engine with a sophisticated ML Model to detect legal risks across multiple categories.

SLM-Powered Optimization: Replaced traditional BERT models with optimized Small Language Models (SLMs) like T5 and BART for faster inference and better contextual understanding of legal clauses.

Actionable Document Editing: Beyond just identifying risks, the system suggests specific textual fixes. Users can select suggestions to automatically modify the contract and download a corrected .docx file.

Multi-Format Support: Robust text extraction from PDF, DOCX, and TXT files using specialized processors.

Risk Categorization: Automatically identifies risks such as Auto-Renewal, Liability, Termination, IP Ownership, and Indemnification.

🏗️ System Architecture
The project follows a modern decoupled architecture:

Frontend: A responsive React application built with Vite and TypeScript, utilizing Lucide React for iconography and Vite for optimized builds.

Backend: A high-performance FastAPI server managing document processing, AI model inference, and the editing service.

AI Layer: A hybrid pipeline utilizing SpaCy for NLP tasks and HuggingFace Transformers for SLM-driven clause analysis.

🛠️ Tech Stack
Backend
Framework: FastAPI

AI/ML: PyTorch, Transformers (T5, BART, Pegasus), SpaCy, Scikit-learn

Document Handling: python-docx, PyPDF2, pdfplumber

Database: SQLAlchemy, Alembic (for future-proofing)

Frontend
Library: React.js (TypeScript)

Styling: CSS Modules

Icons: Lucide React

📥 Installation & Setup
Prerequisites
Python 3.12+

Node.js & npm

Backend Setup
Navigate to the backend directory:

Bash
cd backend
Create and activate a virtual environment:

Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies (ensure numpy is version 1.26.4 and passlib is 1.7.4):

Bash
pip install -r requirements.txt
Run the server:

Bash
uvicorn app.main:app --reload
Frontend Setup
Navigate to the frontend directory:

Bash
cd frontend
Install packages:

Bash
npm install
Start the development server:

Bash
npm run dev
📝 Usage
Upload: Select a legal contract (PDF/DOCX) via the dashboard.

Analyze: The HybridRiskAnalyzer scans the text for specific legal risks and provides a confidence score.

Review: View identified risks in the Analysis Results tab, including descriptions and AI-generated suggestions.

Edit: Use the Smart Editor to select improvements and download the finalized, corrected contract.

🎓 Research Foundation
This project is grounded in contemporary AI & Law research, specifically drawing from:

Savelka, J., & Ashley, K. D. (2023). "The unreasonable effectiveness of large language models in zero-shot semantic annotation of legal texts."

The implementation of SLMs in this repository validates the paper's findings regarding the efficiency of generative models in handling legal datasets like CUAD.
