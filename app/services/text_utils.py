import re
from typing import List

SECTION_PATTERNS = [
    "abstract", "background", "introduction", "objective", "objectives", "methods",
    "materials and methods", "results", "discussion", "conclusion", "conclusions",
    "findings", "impression", "assessment", "plan", "history", "hospital course",
    "diagnosis", "diagnoses", "treatment", "limitations", "clinical relevance"
]

SECTION_REGEX = re.compile(
    r'(?i)\b(' + "|".join(re.escape(s) for s in SECTION_PATTERNS) + r')\s*:\s*'
)


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def detect_title(text: str) -> str:
    first_block = text.strip().split("\n\n", 1)[0].strip()
    lines = [line.strip() for line in first_block.splitlines() if line.strip()]
    if not lines:
        return "Biomedical Summary"
    title = max(lines[:3], key=len)
    return title[:180]


def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)
    sentences = [p.strip() for p in parts if len(p.strip()) > 20]
    return sentences


def split_sections(text: str) -> List[dict]:
    text = normalize_whitespace(text)

    matches = list(SECTION_REGEX.finditer(text))
    if matches:
        sections = []
        for i, match in enumerate(matches):
            section_title = match.group(1).lower()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_text = text[start:end].strip()
            if section_text:
                sections.append({"title": section_title, "text": section_text})
        if sections:
            return sections

    lines = [line.rstrip() for line in text.splitlines()]
    sections = []
    current_title = "general"
    current_lines: List[str] = []

    def flush() -> None:
        nonlocal current_lines, current_title
        body = "\n".join(current_lines).strip()
        if body:
            sections.append({"title": current_title.lower(), "text": body})
        current_lines = []

    for raw in lines:
        line = raw.strip()
        if not line:
            current_lines.append("")
            continue
        normalized = re.sub(r"[:\-\s]+$", "", line).strip().lower()
        if normalized in SECTION_PATTERNS and len(line) <= 40:
            flush()
            current_title = normalized
            continue
        current_lines.append(raw)

    flush()
    return sections or [{"title": "general", "text": text}]