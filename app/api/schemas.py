from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceSpan(BaseModel):
    sentence: str
    section: str = "unknown"
    score: float


class BiomedicalEntity(BaseModel):
    text: str
    label: str


class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=50, description="Biomedical text to summarize")
    target_sentences: int = Field(default=6, ge=3, le=12)
    abstractive: bool = Field(default=False)


class SummaryResponse(BaseModel):
    title: Optional[str] = None
    structured_summary: Dict[str, str]
    extractive_summary: str
    final_summary: str
    key_entities: List[BiomedicalEntity]
    evidence: List[EvidenceSpan]
    warnings: List[str] = Field(default_factory=list)
    stats: Dict[str, Any]