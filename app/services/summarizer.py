from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.api.schemas import EvidenceSpan, SummaryResponse
from app.services.biomedical_entities import extract_entities
from app.services.text_utils import (
    detect_title,
    normalize_whitespace,
    split_sections,
    split_sentences,
)

STOPWORDS = {
    "the", "and", "or", "of", "in", "to", "a", "an", "for", "on", "with", "was", "were",
    "is", "are", "by", "that", "this", "from", "as", "at", "it", "be", "has", "have", "had",
    "we", "our", "their", "patients", "study", "data", "using", "used", "than", "which", "can",
    "may", "into", "also", "these", "those", "such", "between", "within", "after", "before"
}

SECTION_WEIGHTS = {
    "objective": 1.25,
    "objectives": 1.25,
    "abstract": 1.20,
    "methods": 1.10,
    "results": 1.35,
    "findings": 1.35,
    "impression": 1.30,
    "assessment": 1.25,
    "conclusion": 1.30,
    "conclusions": 1.30,
    "clinical relevance": 1.25,
    "limitations": 1.05,
    "general": 1.00,
}

BIOMEDICAL_BOOST_TERMS = {
    "significant", "risk", "reduced", "improved", "mortality", "survival",
    "diagnosis", "treatment", "outcome", "efficacy", "sensitivity",
    "specificity", "adverse", "complication", "trial", "cohort",
    "patients", "intervention", "association", "biomarker", "therapy",
}


@dataclass
class SentenceInfo:
    sentence: str
    section: str
    idx: int
    tokens: List[str]
    score: float = 0.0


class BiomedicalSummarizer:
    def __init__(self) -> None:
        self._abstractive_available = False
        self._tokenizer = None
        self._model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        try:
            print("Loading transformer summarization model...")
            model_path = "./biomed_summarizer"

            self._tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            self._model.to(self._device)
            self._model.eval()

            self._abstractive_available = True
            print("Transformer summarizer loaded successfully.")

        except Exception as e:
            print("Transformer summarizer could not be loaded:", e)
            self._abstractive_available = False
            self._tokenizer = None
            self._model = None

    def _tokenize(self, text: str) -> List[str]:
        tokens = []
        current = []

        for ch in text.lower():
            if ch.isalnum() or ch in "-%":
                current.append(ch)
            elif current:
                token = "".join(current)
                if len(token) > 2 and token not in STOPWORDS:
                    tokens.append(token)
                current = []

        if current:
            token = "".join(current)
            if len(token) > 2 and token not in STOPWORDS:
                tokens.append(token)

        return tokens

    def _prepare_sentences(self, text: str) -> List[SentenceInfo]:
        sections = split_sections(text)
        infos: List[SentenceInfo] = []
        idx = 0

        for section in sections:
            for sent in split_sentences(section["text"]):
                infos.append(
                    SentenceInfo(
                        sentence=sent,
                        section=section["title"],
                        idx=idx,
                        tokens=self._tokenize(sent),
                    )
                )
                idx += 1

        return infos

    def _idf(self, docs: List[List[str]]) -> Dict[str, float]:
        n = max(len(docs), 1)
        df = Counter()

        for doc in docs:
            for token in set(doc):
                df[token] += 1

        return {term: math.log((1 + n) / (1 + freq)) + 1.0 for term, freq in df.items()}

    def _score_sentences(self, infos: List[SentenceInfo]) -> None:
        corpus = [s.tokens for s in infos if s.tokens]
        idf = self._idf(corpus)
        global_freq = Counter(token for sent in corpus for token in sent)

        for info in infos:
            if not info.tokens:
                info.score = 0.0
                continue

            tfidf_sum = sum(
                (1 + math.log(info.tokens.count(tok))) * idf.get(tok, 1.0)
                for tok in set(info.tokens)
            )

            topic_overlap = sum(global_freq.get(tok, 0) for tok in set(info.tokens)) / max(len(info.tokens), 1)
            biomedical_boost = sum(1 for tok in info.tokens if tok in BIOMEDICAL_BOOST_TERMS) * 0.35
            numeric_boost = 0.2 if any(ch.isdigit() for ch in info.sentence) else 0.0
            section_boost = SECTION_WEIGHTS.get(info.section, 1.0)
            length_penalty = 0.95 if len(info.tokens) > 60 else 1.0

            info.score = (
                (tfidf_sum * 0.35 + topic_overlap * 0.25 + biomedical_boost + numeric_boost)
                * section_boost
                * length_penalty
            )

    def _redundancy(self, a: SentenceInfo, b: SentenceInfo) -> float:
        sa, sb = set(a.tokens), set(b.tokens)
        if not sa or not sb:
            return 0.0
        return len(sa & sb) / max(len(sa | sb), 1)

    def _select(self, infos: List[SentenceInfo], target_sentences: int) -> List[SentenceInfo]:
        self._score_sentences(infos)
        ranked = sorted(infos, key=lambda x: x.score, reverse=True)
        selected: List[SentenceInfo] = []

        for candidate in ranked:
            if len(selected) >= target_sentences:
                break
            if any(self._redundancy(candidate, chosen) > 0.6 for chosen in selected):
                continue
            selected.append(candidate)

        return sorted(selected, key=lambda x: x.idx)

    def _structured(self, selected: List[SentenceInfo]) -> Dict[str, str]:
        mapping = {
            "objective": [],
            "methods": [],
            "results": [],
            "conclusion": [],
            "limitations": [],
            "clinical_relevance": [],
        }

        for info in selected:
            section = info.section

            if section in {"objective", "objectives", "background", "introduction", "abstract"}:
                mapping["objective"].append(info.sentence)
            elif section in {"methods", "materials and methods"}:
                mapping["methods"].append(info.sentence)
            elif section in {"results", "findings", "assessment", "impression"}:
                mapping["results"].append(info.sentence)
            elif section in {"conclusion", "conclusions", "discussion", "plan"}:
                mapping["conclusion"].append(info.sentence)
            elif section == "limitations":
                mapping["limitations"].append(info.sentence)
            else:
                mapping["clinical_relevance"].append(info.sentence)

        return {k: " ".join(v[:2]).strip() for k, v in mapping.items() if v}

    def _generate_abstractive_summary(self, text: str) -> str:
        if not self._abstractive_available or self._tokenizer is None or self._model is None:
            raise RuntimeError("Abstractive model is not available.")

        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding=False,
        )

        input_ids = inputs["input_ids"].to(self._device)
        attention_mask = inputs["attention_mask"].to(self._device)

        with torch.no_grad():
            summary_ids = self._model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=150,
                min_length=40,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )

        return self._tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    def summarize(
        self,
        raw_text: str,
        target_sentences: int = 6,
        abstractive: bool = False,
    ) -> SummaryResponse:
        text = normalize_whitespace(raw_text)
        title = detect_title(text)
        infos = self._prepare_sentences(text)

        if len(infos) < 3:
            raise ValueError("Input is too short for reliable summarization.")

        chosen = self._select(infos, target_sentences)
        extractive = " ".join(info.sentence for info in chosen)

        final_summary = extractive
        warnings: List[str] = []

        if abstractive:
            if self._abstractive_available:
                try:
                    abstractive_input = text if len(text) <= 4000 else extractive
                    final_summary = self._generate_abstractive_summary(abstractive_input)
                except Exception as e:
                    warnings.append(
                        f"Abstractive summarization failed: {str(e)}. Returned extractive summary only."
                    )
                    final_summary = extractive
            else:
                warnings.append(
                    "Abstractive mode requested, but no local abstractive model is configured. Returned extractive summary only."
                )

        entities = extract_entities(text)
        structured = self._structured(chosen)

        evidence = [
            EvidenceSpan(
                sentence=info.sentence,
                section=info.section,
                score=round(info.score, 4),
            )
            for info in sorted(chosen, key=lambda x: x.score, reverse=True)
        ]

        stats = {
            "input_characters": len(text),
            "input_sentences": len(infos),
            "summary_sentences": len(chosen),
            "entities_found": len(entities),
            "abstractive_model_loaded": self._abstractive_available,
        }

        return SummaryResponse(
            title=title,
            structured_summary=structured,
            extractive_summary=extractive,
            final_summary=final_summary,
            key_entities=entities,
            evidence=evidence,
            warnings=warnings,
            stats=stats,
        )