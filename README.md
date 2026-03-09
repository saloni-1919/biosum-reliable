# BioSum Reliable

A simple, deployable biomedical text summarization project built with Python, FastAPI, and a lightweight evidence-backed NLP pipeline.

## What it does
- Accepts biomedical text from the UI or API.
- Detects common biomedical sections like Objective, Methods, Results, and Conclusion.
- Generates an extractive summary with evidence spans.
- Extracts basic biomedical entities such as diseases, drugs, procedures, and measures.
- Serves a simple frontend UI from FastAPI.

## Why this version is practical today
This starter is intentionally designed to deploy cleanly today with minimal dependency risk. It does not require GPU, model downloads, or heavy clinical packages to run. That makes it reliable for interviews, demos, and same-day submission.

## Tech stack
- Python 3.11
- FastAPI
- Pydantic
- Jinja2 + vanilla JS frontend
- Lightweight biomedical NLP heuristics

## Project structure
```text
app/
  api/
  core/
  services/
  static/
  templates/
tests/
```

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`

## Run tests
```bash
pytest
```

## Docker
```bash
docker build -t biosum-reliable .
docker run -p 8000:8000 biosum-reliable
```

## API example
### Health
`GET /api/health`

### Summarize
`POST /api/summarize`

```json
{
  "text": "Objective ... Methods ... Results ... Conclusion ...",
  "target_sentences": 6,
  "abstractive": false
}
```

## Deployment
This project is ready for Render, Railway, Azure Web App, Fly.io, or a VPS with Docker.

## Upgrade path
For a stronger next version, add:
- scispaCy entity linking
- PubMed fine-tuned transformer summarizer
- FAISS retrieval
- MLflow experiment tracking
- PDF parsing with Docling or PyMuPDF
