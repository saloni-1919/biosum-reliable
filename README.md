BioSum Reliable
AI-powered biomedical text summarization with evidence-backed insights.
Overview
BioSum Reliable is an intelligent biomedical NLP system that transforms complex research documents into structured summaries. The platform combines extractive NLP techniques with transformer-based abstractive summarization to generate concise and interpretable summaries of biomedical literature. The system also highlights supporting evidence sentences and extracts key biomedical entities such as diseases, drugs, and clinical measurements.
Features
•	Evidence-based extractive summarization
•	Transformer-based abstractive summarization
•	Biomedical entity extraction
•	Structured research summaries (Objective, Methods, Results, Conclusion)
•	Evidence scoring for transparency
•	FastAPI REST API
•	Swagger interactive API documentation
•	Docker-ready deployment
Example Output
Structured Research Summary Example:
Objective: This study evaluated metformin response in adults with diabetes.
Methods: We reviewed 100 patients and compared baseline glucose and HbA1c values.
Results: HbA1c improved after treatment and fewer patients required insulin rescue therapy.
Conclusion: Metformin improved glycemic control in this cohort.
System Architecture
1.	Input biomedical research text
2.	Sentence segmentation and preprocessing
3.	Biomedical entity extraction
4.	Evidence-based sentence scoring
5.	Extractive summarization
6.	Transformer-based abstractive summarization
7.	Structured summary generation
8.	Final summary with supporting evidence
Technology Stack
•	Python
•	FastAPI
•	PyTorch
•	HuggingFace Transformers
•	spaCy NLP
•	Uvicorn ASGI Server
Model Training
Dataset: PubMed Scientific Papers Dataset
Base Model: BART Large CNN
Training samples: 200
Validation samples: 50
Epochs: 1
Learning rate: 2e-5
Final training loss: ~2.57
Validation loss: ~1.97
Running the Project
Clone repository:
git clone https://github.com/saloni-1919/biosum-reliable.git
cd biosum-reliable
Install dependencies:
pip install -r requirements.txt
Run API server:
uvicorn app.main:app --reload
Open API documentation:
http://127.0.0.1:8000/docs
Example API Request

POST /api/summarize

{
"text": "Biomedical research text...",
"target_sentences": 5,
"abstractive": true
}

Project Structure

biosum-reliable
│
├── app
│   ├── main.py
│   ├── services
│   ├── templates
│   └── static
│
├── tests
├── requirements.txt
├── Dockerfile
├── pyproject.toml
└── README.md

Author
Saloni Nathani
