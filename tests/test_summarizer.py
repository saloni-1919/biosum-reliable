from app.services.summarizer import BiomedicalSummarizer


def test_summarizer_basic():
    text = """
    Objective
    This study evaluated metformin response in adults with diabetes.

    Methods
    We reviewed 100 patients and compared baseline glucose and HbA1c values.

    Results
    HbA1c improved after treatment and fewer patients required insulin rescue therapy.

    Conclusion
    Metformin improved glycemic control in this cohort.
    """

    model = BiomedicalSummarizer()
    result = model.summarize(text, target_sentences=4, abstractive=False)

    assert len(result.final_summary) > 20
    assert len(result.evidence) > 0