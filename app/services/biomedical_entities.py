import re
from collections import OrderedDict
from typing import List

from app.api.schemas import BiomedicalEntity


ENTITY_RULES = {
    "DISEASE": [
        r"\b(?:cancer|carcinoma|tumou?r|tumor|diabetes|covid-19|covid|influenza|pneumonia|stroke|sepsis|hypertension|asthma|infection|heart failure|myocardial infarction)\b",
    ],
    "DRUG": [
        r"\b(?:aspirin|metformin|insulin|ibuprofen|paracetamol|acetaminophen|warfarin|heparin|amoxicillin|dexamethasone|remdesivir)\b",
    ],
    "PROCEDURE": [
        r"\b(?:mri|ct scan|computed tomography|ultrasound|biopsy|surgery|intubation|ventilation|transplant|dialysis|chemotherapy|radiotherapy)\b",
    ],
    "MEASURE": [
        r"\b(?:blood pressure|heart rate|bmi|glucose|hemoglobin|creatinine|platelet count|oxygen saturation|spo2|hbA1c)\b",
    ],
}


ABBREVIATION_PATTERN = re.compile(r"\b([A-Z]{2,8})\b")


def extract_entities(text: str, max_items: int = 20) -> List[BiomedicalEntity]:
    found = OrderedDict()
    lowered = text.lower()
    for label, patterns in ENTITY_RULES.items():
        for pattern in patterns:
            for match in re.finditer(pattern, lowered, flags=re.IGNORECASE):
                token = match.group(0)
                key = (token.lower(), label)
                if key not in found:
                    found[key] = BiomedicalEntity(text=token, label=label)
    for match in ABBREVIATION_PATTERN.finditer(text):
        token = match.group(1)
        if token not in {"DNA", "RNA"} and len(found) >= max_items:
            break
        if len(token) >= 3:
            key = (token, "ABBREVIATION")
            found.setdefault(key, BiomedicalEntity(text=token, label="ABBREVIATION"))
    return list(found.values())[:max_items]
