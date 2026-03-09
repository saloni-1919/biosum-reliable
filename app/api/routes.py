from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.schemas import SummaryRequest, SummaryResponse
from app.core.config import get_settings
from app.services.summarizer import BiomedicalSummarizer

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
summarizer = BiomedicalSummarizer()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": get_settings().app_name})


@router.get("/api/health")
def health():
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@router.post("/api/summarize", response_model=SummaryResponse)
def summarize(payload: SummaryRequest):
    settings = get_settings()
    if len(payload.text) > settings.max_input_chars:
        raise HTTPException(status_code=413, detail=f"Input too large. Max {settings.max_input_chars} characters.")
    try:
        return summarizer.summarize(payload.text, target_sentences=payload.target_sentences, abstractive=payload.abstractive)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/summarize-file", response_model=SummaryResponse)
async def summarize_file(file: UploadFile = File(...), target_sentences: int = 6, abstractive: bool = False):
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=415, detail="Only UTF-8 text files are supported in this starter deployment.")
    try:
        return summarizer.summarize(text, target_sentences=target_sentences, abstractive=abstractive)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
